"""
Notification Write-Through Cache Service

This module provides a write-through cache implementation with Bloom filter optimization
for notification handling.
"""

from typing import Dict, Any, Optional, List, Set
import asyncio
import json
from datetime import datetime, timedelta
import hashlib
from array import array
import zlib
from collections import defaultdict
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class BloomFilter:
    def __init__(self, size: int, hash_count: int):
        self.size = size
        self.hash_count = hash_count
        # Use array of unsigned bytes (B) for bit storage
        self.bit_array = array('B', [0] * ((size + 7) // 8))

    def _get_bit(self, index: int) -> bool:
        """Get the value of a bit at the given index."""
        byte_index = index // 8
        bit_index = index % 8
        return bool(self.bit_array[byte_index] & (1 << bit_index))

    def _set_bit(self, index: int):
        """Set the bit at the given index to 1."""
        byte_index = index // 8
        bit_index = index % 8
        self.bit_array[byte_index] |= (1 << bit_index)

    def add(self, item: str):
        """Add an item to the Bloom filter."""
        for seed in range(self.hash_count):
            hash_obj = hashlib.sha256(f"{item}{seed}".encode())
            index = int(hash_obj.hexdigest(), 16) % self.size
            self._set_bit(index)

    def check(self, item: str) -> bool:
        """Check if an item might be in the set."""
        for seed in range(self.hash_count):
            hash_obj = hashlib.sha256(f"{item}{seed}".encode())
            index = int(hash_obj.hexdigest(), 16) % self.size
            if not self._get_bit(index):
                return False
        return True

    def merge(self, other: 'BloomFilter'):
        """Merge another Bloom filter into this one."""
        if self.size != other.size:
            raise ValueError("Bloom filters must have same size")
        for i in range(len(self.bit_array)):
            self.bit_array[i] |= other.bit_array[i]

    def compress(self) -> bytes:
        """Compress the Bloom filter for storage."""
        return zlib.compress(self.bit_array.tobytes())

    @classmethod
    def decompress(cls, data: bytes, size: int, hash_count: int) -> 'BloomFilter':
        """Create a Bloom filter from compressed data."""
        bf = cls(size, hash_count)
        bf.bit_array = array('B', zlib.decompress(data))
        return bf

class WriteThruCache:
    def __init__(
        self,
        cache_service,
        shard_manager,
        db: AsyncSession,
        bloom_size: int = 100000,
        bloom_hashes: int = 5
    ):
        self.settings = get_settings()
        self.cache_service = cache_service
        self.shard_manager = shard_manager
        self.db = db
        self.write_queue = asyncio.Queue()
        self.processing = False
        self.batch_size = 100
        self.flush_interval = 1  # seconds
        self.compression_threshold = 1024  # bytes
        self.bloom_filters = {
            'exists': BloomFilter(bloom_size, bloom_hashes),
            'deleted': BloomFilter(bloom_size, bloom_hashes)
        }
        self.stats = defaultdict(int)
        self.last_sync = datetime.utcnow()

    async def start(self):
        """Start write-through processing."""
        self.processing = True
        asyncio.create_task(self._process_write_queue())
        asyncio.create_task(self._sync_bloom_filters())
        asyncio.create_task(self._monitor_stats())

    async def stop(self):
        """Stop write-through processing."""
        self.processing = False
        # Flush remaining writes
        await self._flush_writes()

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get item with Bloom filter optimization."""
        # Check deletion Bloom filter
        if self.bloom_filters['deleted'].check(key):
            self.stats['bloom_deleted_hits'] += 1
            return None

        # Check cache first
        value = await self.cache_service.get_notification(key)
        if value is not None:
            self.stats['cache_hits'] += 1
            return value

        # Check existence Bloom filter
        if not self.bloom_filters['exists'].check(key):
            self.stats['bloom_missing_hits'] += 1
            return None

        # Try database
        value = await self._get_from_db(key)
        if value is not None:
            self.stats['db_hits'] += 1
            # Update cache
            await self.cache_service.cache_notification(key, value)
            # Update Bloom filter
            self.bloom_filters['exists'].add(key)
        else:
            self.stats['db_misses'] += 1

        return value

    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None):
        """Set item with write-through."""
        # Compress if beneficial
        if len(json.dumps(value)) > self.compression_threshold:
            value = self._compress_value(value)

        # Update cache immediately
        await self.cache_service.cache_notification(key, value, ttl)
        
        # Queue database write
        await self.write_queue.put({
            'operation': 'set',
            'key': key,
            'value': value,
            'timestamp': datetime.utcnow().isoformat()
        })

        # Update Bloom filter
        self.bloom_filters['exists'].add(key)
        self.stats['write_operations'] += 1

    async def delete(self, key: str):
        """Delete item with write-through."""
        # Delete from cache immediately
        await self.cache_service.delete_notification(key)
        
        # Queue database delete
        await self.write_queue.put({
            'operation': 'delete',
            'key': key,
            'timestamp': datetime.utcnow().isoformat()
        })

        # Update Bloom filters
        self.bloom_filters['deleted'].add(key)
        self.stats['delete_operations'] += 1

    async def _process_write_queue(self):
        """Process queued writes in batches."""
        while self.processing:
            try:
                batch = []
                try:
                    # Get first item
                    item = await asyncio.wait_for(
                        self.write_queue.get(),
                        timeout=self.flush_interval
                    )
                    batch.append(item)
                    
                    # Try to get more items
                    while len(batch) < self.batch_size:
                        try:
                            item = self.write_queue.get_nowait()
                            batch.append(item)
                        except asyncio.QueueEmpty:
                            break
                    
                except asyncio.TimeoutError:
                    continue

                # Process batch
                await self._write_batch_to_db(batch)
                
                # Update stats
                self.stats['batches_processed'] += 1
                self.stats['items_processed'] += len(batch)

            except Exception as e:
                logger.error(f"Error processing write batch: {str(e)}")
                await asyncio.sleep(1)

    async def _write_batch_to_db(self, batch: List[Dict[str, Any]]):
        """Write a batch of operations to database."""
        async with self.db.begin() as transaction:
            try:
                for item in batch:
                    if item['operation'] == 'set':
                        await self.db.execute(
                            text("""
                                INSERT INTO notifications (id, data, created_at)
                                VALUES (:key, :value, :timestamp)
                                ON CONFLICT (id) DO UPDATE
                                SET data = :value, updated_at = :timestamp
                            """),
                            {
                                'key': item['key'],
                                'value': json.dumps(item['value']),
                                'timestamp': item['timestamp']
                            }
                        )
                    elif item['operation'] == 'delete':
                        await self.db.execute(
                            text("DELETE FROM notifications WHERE id = :key"),
                            {'key': item['key']}
                        )
                
                await transaction.commit()
                self.stats['successful_writes'] += len(batch)
                
            except Exception as e:
                await transaction.rollback()
                logger.error(f"Database write error: {str(e)}")
                self.stats['failed_writes'] += len(batch)
                # Requeue failed items
                for item in batch:
                    await self.write_queue.put(item)

    async def _get_from_db(self, key: str) -> Optional[Dict[str, Any]]:
        """Get item from database."""
        try:
            result = await self.db.execute(
                text("SELECT data FROM notifications WHERE id = :key"),
                {'key': key}
            )
            row = result.first()
            if row:
                return json.loads(row[0])
        except Exception as e:
            logger.error(f"Database read error: {str(e)}")
            self.stats['db_errors'] += 1
        return None

    async def _sync_bloom_filters(self):
        """Periodically sync Bloom filters across instances."""
        while self.processing:
            try:
                # Get Bloom filters from other instances
                compressed_filters = await self.shard_manager.get('bloom_filters')
                if compressed_filters:
                    other_filters = {
                        key: BloomFilter.decompress(data, self.bloom_filters[key].size, self.bloom_filters[key].hash_count)
                        for key, data in compressed_filters.items()
                    }
                    
                    # Merge filters
                    for key, bf in self.bloom_filters.items():
                        bf.merge(other_filters[key])

                # Store our filters
                await self.shard_manager.set(
                    'bloom_filters',
                    {key: bf.compress() for key, bf in self.bloom_filters.items()},
                    ttl=300  # 5 minutes
                )

                self.stats['bloom_syncs'] += 1
                await asyncio.sleep(60)  # Sync every minute

            except Exception as e:
                logger.error(f"Error syncing Bloom filters: {str(e)}")
                await asyncio.sleep(30)

    async def _monitor_stats(self):
        """Monitor and log cache statistics."""
        while self.processing:
            try:
                total_ops = self.stats['write_operations'] + self.stats['delete_operations']
                if total_ops > 0:
                    logger.info(
                        "Write-through stats: "
                        f"Success Rate: {self.stats['successful_writes']/total_ops:.2%}, "
                        f"Cache Hit Rate: {self.stats['cache_hits']/(self.stats['cache_hits'] + self.stats['db_hits']):.2%}, "
                        f"Bloom Filter Efficiency: {(self.stats['bloom_deleted_hits'] + self.stats['bloom_missing_hits'])/total_ops:.2%}"
                    )

                await asyncio.sleep(300)  # Log every 5 minutes
            except Exception as e:
                logger.error(f"Error monitoring stats: {str(e)}")
                await asyncio.sleep(60)

    def _compress_value(self, value: Dict[str, Any]) -> Dict[str, Any]:
        """Compress large values."""
        try:
            serialized = json.dumps(value)
            compressed = zlib.compress(serialized.encode())
            if len(compressed) < len(serialized):
                return {
                    'compressed': True,
                    'data': compressed
                }
        except Exception as e:
            logger.error(f"Compression error: {str(e)}")
        return value

    async def _flush_writes(self):
        """Flush all pending writes."""
        batch = []
        while not self.write_queue.empty():
            try:
                item = self.write_queue.get_nowait()
                batch.append(item)
            except asyncio.QueueEmpty:
                break
        
        if batch:
            await self._write_batch_to_db(batch)

# Alias WriteThruCache as NotificationWriteThrough for backward compatibility
NotificationWriteThrough = WriteThruCache 
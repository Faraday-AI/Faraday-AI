import numpy as np
import tensorflow as tf
import networkx as nx
import openai
from typing import Dict, Any, List, Optional, Set
from app.core.config import get_settings
import logging
from functools import lru_cache
from datetime import datetime, timedelta
import asyncio
from fastapi import WebSocket, HTTPException
import json
import jwt
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import time
from collections import defaultdict
import prometheus_client as prom

logger = logging.getLogger(__name__)
settings = get_settings()

# Prometheus metrics
ws_connections = prom.Gauge('ws_active_connections', 'Number of active WebSocket connections')
ws_messages = prom.Counter('ws_messages_total', 'Total WebSocket messages', ['type'])
ws_errors = prom.Counter('ws_errors_total', 'Total WebSocket errors', ['type'])
ws_latency = prom.Histogram('ws_message_latency_seconds', 'WebSocket message latency')

class RateLimiter:
    def __init__(self, rate_limit: int = 60, time_window: int = 60):
        self.rate_limit = rate_limit  # messages per time window
        self.time_window = time_window  # time window in seconds
        self.message_counts = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        current_time = time.time()
        # Remove old messages outside the time window
        self.message_counts[user_id] = [
            timestamp for timestamp in self.message_counts[user_id]
            if current_time - timestamp < self.time_window
        ]
        
        # Check if under rate limit
        if len(self.message_counts[user_id]) < self.rate_limit:
            self.message_counts[user_id].append(current_time)
            return True
        return False

class ConnectionMetrics:
    def __init__(self):
        self.start_time = time.time()
        self.message_count = 0
        self.error_count = 0
        self.last_message_time = None
        self.latencies = []

class WSConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, Set[WebSocket]]] = {}
        self.user_sessions: Dict[str, Set[str]] = {}
        self.rate_limiter = RateLimiter()
        self.connection_pools: Dict[str, List[WebSocket]] = {}
        self.max_pool_size = 1000
        self.recovery_data: Dict[str, Dict[str, Any]] = {}
        self.connection_metrics: Dict[str, Dict[str, ConnectionMetrics]] = {}
        self.health_check_interval = 30  # seconds
        self._start_health_check()

    def _start_health_check(self):
        """Start periodic health check for connections."""
        asyncio.create_task(self._periodic_health_check())

    async def _periodic_health_check(self):
        """Perform periodic health check on all connections."""
        while True:
            try:
                dead_connections = []
                for session_id, connections in self.active_connections.items():
                    for role, websockets in connections.items():
                        for websocket in websockets:
                            try:
                                await websocket.send_json({"type": "ping"})
                            except Exception as e:
                                logger.warning(f"Health check failed for connection in session {session_id}: {str(e)}")
                                dead_connections.append((session_id, role, websocket))

                # Clean up dead connections
                for session_id, role, websocket in dead_connections:
                    await self._handle_connection_failure(session_id, role, websocket)

                # Update metrics
                ws_connections.set(sum(
                    len(connections["teachers"]) + len(connections["observers"])
                    for connections in self.active_connections.values()
                ))

            except Exception as e:
                logger.error(f"Error in health check: {str(e)}")

            await asyncio.sleep(self.health_check_interval)

    async def _handle_connection_failure(
        self,
        session_id: str,
        role: str,
        websocket: WebSocket
    ):
        """Handle failed connection cleanup."""
        try:
            if session_id in self.active_connections:
                self.active_connections[session_id][role].discard(websocket)
                if websocket in self.connection_pools[session_id]:
                    self.connection_pools[session_id].remove(websocket)
                
                # Update metrics
                ws_errors.labels(type='connection_failure').inc()
                
                # Log connection statistics
                if session_id in self.connection_metrics:
                    metrics = self.connection_metrics[session_id].get(str(id(websocket)))
                    if metrics:
                        duration = time.time() - metrics.start_time
                        avg_latency = sum(metrics.latencies) / len(metrics.latencies) if metrics.latencies else 0
                        logger.info(
                            f"Connection stats - Duration: {duration:.2f}s, "
                            f"Messages: {metrics.message_count}, "
                            f"Errors: {metrics.error_count}, "
                            f"Avg Latency: {avg_latency:.3f}s"
                        )
        except Exception as e:
            logger.error(f"Error handling connection failure: {str(e)}")

    async def connect(
        self,
        session_id: str,
        websocket: WebSocket,
        user_id: str,
        role: str
    ):
        """Connect and authenticate a WebSocket client with rate limiting and monitoring."""
        try:
            # Initialize connection metrics
            if session_id not in self.connection_metrics:
                self.connection_metrics[session_id] = {}
            self.connection_metrics[session_id][str(id(websocket))] = ConnectionMetrics()

            # Existing connection logic
            if not self.rate_limiter.is_allowed(user_id):
                ws_errors.labels(type='rate_limit_exceeded').inc()
                await websocket.close(code=4029)
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            if len(self.connection_pools.get(session_id, [])) >= self.max_pool_size:
                ws_errors.labels(type='pool_full').inc()
                await websocket.close(code=4503)
                raise HTTPException(status_code=503, detail="Connection pool full")

            await websocket.accept()
            
            # Update connection tracking
            if session_id not in self.active_connections:
                self.active_connections[session_id] = {
                    "teachers": set(),
                    "observers": set()
                }
                self.connection_pools[session_id] = []
            
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = set()
                
            self.user_sessions[user_id].add(session_id)
            self.connection_pools[session_id].append(websocket)
            
            if role == "teacher":
                self.active_connections[session_id]["teachers"].add(websocket)
            else:
                self.active_connections[session_id]["observers"].add(websocket)

            # Update metrics
            ws_connections.inc()
            
            # Store recovery data
            self.recovery_data[session_id] = {
                "last_message": None,
                "user_id": user_id,
                "role": role,
                "connected_at": datetime.now().isoformat()
            }

        except Exception as e:
            ws_errors.labels(type='connection_error').inc()
            logger.error(f"Error in connect: {str(e)}")
            raise

    async def disconnect(
        self,
        session_id: str,
        websocket: WebSocket,
        user_id: str,
        role: str
    ):
        """Disconnect a WebSocket client and clean up resources."""
        if session_id in self.active_connections:
            if role == "teacher":
                self.active_connections[session_id]["teachers"].discard(websocket)
            else:
                self.active_connections[session_id]["observers"].discard(websocket)
            
            self.connection_pools[session_id].remove(websocket)
                
            if not (self.active_connections[session_id]["teachers"] or 
                   self.active_connections[session_id]["observers"]):
                del self.active_connections[session_id]
                del self.connection_pools[session_id]
                del self.recovery_data[session_id]
        
        if user_id in self.user_sessions:
            self.user_sessions[user_id].discard(session_id)
            if not self.user_sessions[user_id]:
                del self.user_sessions[user_id]

    async def broadcast(
        self,
        session_id: str,
        message: Dict[str, Any],
        role: Optional[str] = None
    ):
        """Broadcast message to connected clients with monitoring."""
        if session_id not in self.active_connections:
            return
            
        start_time = time.time()
        connections = self.active_connections[session_id]
        dead_connections = set()
        
        # Store message for recovery
        self.recovery_data[session_id]["last_message"] = {
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Determine target connections based on role
        targets = []
        if role == "teacher":
            targets = connections["teachers"]
        elif role == "observer":
            targets = connections["observers"]
        else:
            targets = connections["teachers"].union(connections["observers"])
        
        # Track broadcast metrics
        successful_broadcasts = 0
        
        for websocket in targets:
            try:
                await websocket.send_json(message)
                successful_broadcasts += 1
                
                # Update connection metrics
                conn_id = str(id(websocket))
                if session_id in self.connection_metrics and conn_id in self.connection_metrics[session_id]:
                    metrics = self.connection_metrics[session_id][conn_id]
                    metrics.message_count += 1
                    metrics.last_message_time = time.time()
                    metrics.latencies.append(time.time() - start_time)
                
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {str(e)}")
                dead_connections.add(websocket)
                ws_errors.labels(type='broadcast_error').inc()
        
        # Update metrics
        ws_messages.labels(type='broadcast').inc()
        ws_latency.observe(time.time() - start_time)
        
        # Clean up dead connections
        for websocket in dead_connections:
            await self._handle_connection_failure(
                session_id,
                "teacher" if websocket in connections["teachers"] else "observer",
                websocket
            )

    async def recover_session(
        self,
        session_id: str,
        websocket: WebSocket,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Recover session state after disconnection."""
        if session_id in self.recovery_data:
            recovery_info = self.recovery_data[session_id]
            if recovery_info["user_id"] == user_id:
                return {
                    "last_message": recovery_info["last_message"],
                    "role": recovery_info["role"],
                    "connected_at": recovery_info["connected_at"]
                }
        return None

class AIGroupAnalysis:
    def __init__(self):
        self.openai_client = openai.Client(api_key=settings.OPENAI_API_KEY)
        self._initialize_models()
        self.active_sessions = {}
        self.interaction_buffer = {}
        self.alert_thresholds = {
            "cohesion": 0.3,
            "participation": 0.4,
            "isolation": 0.2
        }
        self.connection_manager = WSConnectionManager()
        self.security = HTTPBearer()

    def _initialize_models(self):
        """Initialize group dynamics analysis models."""
        self.interaction_model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(50, 50)),  # Interaction matrix
            tf.keras.layers.Conv1D(32, 3, activation='relu'),
            tf.keras.layers.MaxPooling1D(),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(4, activation='softmax')  # 4 interaction types
        ])

    async def analyze_group_dynamics(
        self,
        group_data: Dict[str, Any],
        activity_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyze group dynamics and team interactions."""
        try:
            # Process group interaction data
            interaction_matrix = self._create_interaction_matrix(group_data)
            network = self._build_social_network(interaction_matrix)
            
            # Get AI group analysis
            prompt = f"""
            Analyze group dynamics considering:
            1. Team cohesion
            2. Leadership patterns
            3. Communication effectiveness
            4. Collaboration quality
            5. Social inclusion
            
            Activity Context: {activity_context or 'General PE group activity'}
            
            Provide:
            1. Group dynamics assessment
            2. Team effectiveness analysis
            3. Communication patterns
            4. Improvement recommendations
            5. Intervention strategies
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.7
            )
            
            return {
                "group_metrics": self._analyze_group_metrics(network),
                "ai_insights": response.choices[0].message.content,
                "cohesion_score": self._calculate_cohesion_score(network),
                "recommendations": self._generate_group_recommendations(response),
                "visualizations": self._generate_group_visualizations(network, interaction_matrix)
            }
        except Exception as e:
            logger.error(f"Error analyzing group dynamics: {str(e)}")
            return {"error": str(e)}

    def _create_interaction_matrix(
        self,
        group_data: Dict[str, Any]
    ) -> np.ndarray:
        """Create interaction matrix from group data."""
        n_students = len(group_data.get("students", []))
        matrix = np.zeros((n_students, n_students))
        
        for interaction in group_data.get("interactions", []):
            i, j = interaction["student_ids"]
            weight = interaction.get("strength", 1.0)
            matrix[i][j] = weight
            matrix[j][i] = weight  # Symmetric interactions
            
        return matrix

    def _build_social_network(self, interaction_matrix: np.ndarray) -> nx.Graph:
        """Build social network graph from interaction matrix."""
        G = nx.from_numpy_array(interaction_matrix)
        
        # Calculate network metrics
        nx.set_node_attributes(
            G,
            nx.eigenvector_centrality_numpy(G),
            "centrality"
        )
        nx.set_node_attributes(
            G,
            nx.clustering(G),
            "clustering"
        )
        
        return G

    def _analyze_group_metrics(self, network: nx.Graph) -> Dict[str, Any]:
        """Analyze various group metrics."""
        return {
            "density": float(nx.density(network)),
            "transitivity": float(nx.transitivity(network)),
            "average_clustering": float(nx.average_clustering(network)),
            "average_shortest_path": float(nx.average_shortest_path_length(network)),
            "degree_centrality": {
                str(node): float(cent)
                for node, cent in nx.degree_centrality(network).items()
            }
        }

    def _calculate_cohesion_score(self, network: nx.Graph) -> float:
        """Calculate overall group cohesion score."""
        metrics = self._analyze_group_metrics(network)
        weights = {
            "density": 0.3,
            "transitivity": 0.3,
            "average_clustering": 0.2,
            "average_shortest_path": 0.2
        }
        
        # Normalize path length (inverse relationship with cohesion)
        path_score = 1 / (1 + metrics["average_shortest_path"])
        
        return float(
            weights["density"] * metrics["density"] +
            weights["transitivity"] * metrics["transitivity"] +
            weights["average_clustering"] * metrics["average_clustering"] +
            weights["average_shortest_path"] * path_score
        )

    def _generate_group_recommendations(
        self,
        ai_response: Any
    ) -> List[Dict[str, Any]]:
        """Generate group-specific recommendations."""
        insights = ai_response.choices[0].message.content.split('\n')
        return [
            {
                "area": "group_dynamics",
                "recommendation": insight.strip(),
                "priority": self._calculate_priority(insight),
                "implementation": self._generate_implementation_steps(insight)
            }
            for insight in insights if insight.strip()
        ]

    def _generate_group_visualizations(
        self,
        network: nx.Graph,
        interaction_matrix: np.ndarray
    ) -> Dict[str, Any]:
        """Generate visualizations for group analysis."""
        return {
            "interaction_heatmap": interaction_matrix.tolist(),
            "network_layout": self._generate_network_layout(network),
            "centrality_distribution": self._generate_centrality_distribution(network),
            "clustering_distribution": self._generate_clustering_distribution(network)
        }

    def _calculate_priority(self, insight: str) -> str:
        """Calculate priority level for group recommendations."""
        if "immediate" in insight.lower() or "critical" in insight.lower():
            return "high"
        elif "consider" in insight.lower() or "might" in insight.lower():
            return "medium"
        return "low"

    def _generate_implementation_steps(self, insight: str) -> List[str]:
        """Generate specific implementation steps for recommendations."""
        return [
            f"Step 1: {insight.split(':')[0] if ':' in insight else 'Implement'} strategy",
            "Step 2: Monitor group response",
            "Step 3: Gather feedback",
            "Step 4: Adjust approach",
            "Step 5: Reinforce positive changes"
        ]

    def _generate_network_layout(self, network: nx.Graph) -> Dict[str, List[float]]:
        """Generate network layout for visualization."""
        layout = nx.spring_layout(network)
        return {
            str(node): [float(coord) for coord in pos]
            for node, pos in layout.items()
        }

    def _generate_centrality_distribution(
        self,
        network: nx.Graph
    ) -> Dict[str, List[float]]:
        """Generate centrality distribution data."""
        centralities = {
            "degree": nx.degree_centrality(network),
            "eigenvector": nx.eigenvector_centrality_numpy(network),
            "betweenness": nx.betweenness_centrality(network)
        }
        return {
            metric: [float(val) for val in values.values()]
            for metric, values in centralities.items()
        }

    def _generate_clustering_distribution(
        self,
        network: nx.Graph
    ) -> List[float]:
        """Generate clustering coefficient distribution."""
        return [
            float(coef)
            for coef in nx.clustering(network).values()
        ]

    async def start_real_time_monitoring(
        self,
        session_id: str,
        group_data: Dict[str, Any],
        monitoring_interval: int = 30  # seconds
    ) -> Dict[str, Any]:
        """Start real-time monitoring of group dynamics."""
        try:
            if session_id in self.active_sessions:
                return {"error": "Session already active"}

            self.active_sessions[session_id] = {
                "start_time": datetime.now(),
                "group_data": group_data,
                "interaction_history": [],
                "alerts": [],
                "metrics_history": [],
                "last_update": datetime.now()
            }

            self.interaction_buffer[session_id] = []

            # Start background monitoring task
            asyncio.create_task(
                self._monitor_session(session_id, monitoring_interval)
            )

            return {
                "status": "success",
                "session_id": session_id,
                "message": "Real-time monitoring started"
            }
        except Exception as e:
            logger.error(f"Error starting real-time monitoring: {str(e)}")
            return {"error": str(e)}

    async def update_session_data(
        self,
        session_id: str,
        new_interactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update session with new interaction data."""
        try:
            if session_id not in self.active_sessions:
                return {"error": "Session not found"}

            # Buffer new interactions
            self.interaction_buffer[session_id].extend(new_interactions)

            # Update last interaction time
            self.active_sessions[session_id]["last_update"] = datetime.now()

            return {
                "status": "success",
                "buffered_interactions": len(self.interaction_buffer[session_id])
            }
        except Exception as e:
            logger.error(f"Error updating session data: {str(e)}")
            return {"error": str(e)}

    async def get_session_status(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Get current status of monitoring session."""
        try:
            if session_id not in self.active_sessions:
                return {"error": "Session not found"}

            session = self.active_sessions[session_id]
            current_time = datetime.now()

            return {
                "session_id": session_id,
                "duration": (current_time - session["start_time"]).seconds,
                "last_update": (current_time - session["last_update"]).seconds,
                "total_interactions": len(session["interaction_history"]),
                "recent_alerts": session["alerts"][-5:],
                "current_metrics": session["metrics_history"][-1] if session["metrics_history"] else None
            }
        except Exception as e:
            logger.error(f"Error getting session status: {str(e)}")
            return {"error": str(e)}

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and extract user information."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            return payload
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )

    async def check_session_access(
        self,
        session_id: str,
        user_id: str,
        role: str
    ) -> bool:
        """Check if user has access to the session."""
        if session_id not in self.active_sessions:
            return False
            
        session = self.active_sessions[session_id]
        
        if role == "teacher":
            return user_id in session["group_data"].get("teachers", [])
        elif role == "observer":
            return (user_id in session["group_data"].get("teachers", []) or
                   user_id in session["group_data"].get("observers", []))
        return False

    async def connect_websocket(
        self,
        session_id: str,
        websocket: WebSocket,
        token: str
    ):
        """Connect and authenticate a WebSocket client."""
        try:
            # Verify token and extract user info
            payload = await self.verify_token(token)
            user_id = payload["sub"]
            role = payload["role"]
            
            # Check session access
            if not await self.check_session_access(session_id, user_id, role):
                await websocket.close(code=4003)
                return
            
            # Connect to session
            await self.connection_manager.connect(session_id, websocket, user_id, role)
            
            try:
                # Send initial session state
                if session_id in self.active_sessions:
                    await websocket.send_json({
                        "type": "session_state",
                        "data": await self.get_session_status(session_id)
                    })
                
                # Keep connection alive and handle incoming messages
                while True:
                    data = await websocket.receive_json()
                    await self._handle_websocket_message(
                        session_id,
                        websocket,
                        data,
                        role
                    )
                    
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
            finally:
                await self.connection_manager.disconnect(
                    session_id,
                    websocket,
                    user_id,
                    role
                )
                
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            await websocket.close(code=4000)

    async def _handle_websocket_message(
        self,
        session_id: str,
        websocket: WebSocket,
        data: Dict[str, Any],
        role: str
    ):
        """Handle incoming WebSocket messages with role-based permissions."""
        message_type = data.get("type")
        
        # Teacher-only operations
        if message_type in ["update_interactions", "update_thresholds"] and role != "teacher":
            await websocket.send_json({
                "type": "error",
                "data": {"message": "Insufficient permissions"}
            })
            return
        
        if message_type == "update_interactions":
            await self.update_session_data(session_id, data.get("interactions", []))
        elif message_type == "update_thresholds":
            await self._update_alert_thresholds(session_id, data.get("thresholds", {}))
        elif message_type == "get_status":
            status = await self.get_session_status(session_id)
            await websocket.send_json({
                "type": "session_status",
                "data": status
            })

    async def _broadcast_update(
        self,
        session_id: str,
        update_type: str,
        data: Dict[str, Any],
        role: Optional[str] = None
    ):
        """Broadcast updates to connected clients with role-based filtering."""
        await self.connection_manager.broadcast(session_id, {
            "type": update_type,
            "data": data
        }, role)

    async def _update_alert_thresholds(
        self,
        session_id: str,
        thresholds: Dict[str, float]
    ):
        """Update alert thresholds for a session."""
        if session_id not in self.active_sessions:
            return
            
        session = self.active_sessions[session_id]
        session["alert_thresholds"] = {
            **self.alert_thresholds,
            **thresholds
        }
        
        # Broadcast threshold update to teachers only
        await self._broadcast_update(
            session_id,
            "thresholds_updated",
            {"thresholds": session["alert_thresholds"]},
            role="teacher"
        )

    async def _monitor_session(
        self,
        session_id: str,
        interval: int
    ):
        """Background task for monitoring session."""
        try:
            while session_id in self.active_sessions:
                # Process buffered interactions
                if self.interaction_buffer[session_id]:
                    await self._process_interactions(session_id)
                    
                    # Broadcast interaction update
                    await self._broadcast_update(
                        session_id,
                        "interactions_processed",
                        {
                            "total_interactions": len(self.active_sessions[session_id]["interaction_history"])
                        }
                    )

                # Check for alerts
                previous_alerts = len(self.active_sessions[session_id]["alerts"])
                await self._check_alerts(session_id)
                
                # Broadcast new alerts
                current_alerts = self.active_sessions[session_id]["alerts"]
                if len(current_alerts) > previous_alerts:
                    await self._broadcast_update(
                        session_id,
                        "new_alerts",
                        {
                            "alerts": current_alerts[previous_alerts:]
                        }
                    )

                # Update metrics
                previous_metrics = self.active_sessions[session_id]["metrics_history"][-1] if self.active_sessions[session_id]["metrics_history"] else None
                await self._update_metrics(session_id)
                
                # Broadcast metric updates
                current_metrics = self.active_sessions[session_id]["metrics_history"][-1]
                if current_metrics != previous_metrics:
                    await self._broadcast_update(
                        session_id,
                        "metrics_updated",
                        {
                            "metrics": current_metrics
                        }
                    )

                await asyncio.sleep(interval)
        except Exception as e:
            logger.error(f"Error in monitoring task: {str(e)}")

    async def _process_interactions(
        self,
        session_id: str
    ):
        """Process buffered interactions."""
        session = self.active_sessions[session_id]
        
        # Add buffered interactions to history
        session["interaction_history"].extend(
            self.interaction_buffer[session_id]
        )
        
        # Clear buffer
        self.interaction_buffer[session_id] = []

    async def _check_alerts(
        self,
        session_id: str
    ):
        """Check for alert conditions."""
        session = self.active_sessions[session_id]
        
        # Create interaction matrix from recent interactions
        recent_interactions = session["interaction_history"][-20:]
        if not recent_interactions:
            return

        matrix = self._create_interaction_matrix({
            "students": session["group_data"]["students"],
            "interactions": recent_interactions
        })
        
        network = self._build_social_network(matrix)
        metrics = self._analyze_group_metrics(network)
        
        # Check for alert conditions
        alerts = []
        
        if metrics["density"] < session["alert_thresholds"]["cohesion"]:
            alerts.append({
                "type": "low_cohesion",
                "severity": "high",
                "message": "Group cohesion has dropped significantly"
            })
            
        isolated_students = [
            student["id"]
            for student in session["group_data"]["students"]
            if metrics["degree_centrality"][str(student["id"])] < session["alert_thresholds"]["isolation"]
        ]
        
        if isolated_students:
            alerts.append({
                "type": "student_isolation",
                "severity": "medium",
                "message": f"Students {isolated_students} showing signs of isolation",
                "affected_students": isolated_students
            })
        
        session["alerts"].extend(alerts)

    async def _update_metrics(
        self,
        session_id: str
    ):
        """Update session metrics."""
        session = self.active_sessions[session_id]
        
        # Calculate current metrics
        matrix = self._create_interaction_matrix({
            "students": session["group_data"]["students"],
            "interactions": session["interaction_history"]
        })
        
        network = self._build_social_network(matrix)
        metrics = self._analyze_group_metrics(network)
        
        # Add timestamp
        metrics["timestamp"] = datetime.now().isoformat()
        
        # Store metrics
        session["metrics_history"].append(metrics)

    async def _generate_session_analysis(
        self,
        session: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate final session analysis."""
        try:
            # Calculate overall metrics
            matrix = self._create_interaction_matrix({
                "students": session["group_data"]["students"],
                "interactions": session["interaction_history"]
            })
            
            network = self._build_social_network(matrix)
            
            # Get AI analysis
            prompt = f"""
            Analyze complete group session considering:
            1. Overall interaction patterns
            2. Group development stages
            3. Leadership emergence
            4. Participation balance
            5. Social dynamics evolution

            Session duration: {(datetime.now() - session['start_time']).seconds} seconds
            Total interactions: {len(session['interaction_history'])}
            Alert count: {len(session['alerts'])}

            Provide:
            1. Session effectiveness assessment
            2. Group development analysis
            3. Key observations
            4. Future recommendations
            5. Success indicators
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.7
            )
            
            return {
                "duration": (datetime.now() - session["start_time"]).seconds,
                "total_interactions": len(session["interaction_history"]),
                "alert_summary": self._summarize_alerts(session["alerts"]),
                "metrics_trends": self._analyze_metric_trends(session["metrics_history"]),
                "ai_analysis": response.choices[0].message.content,
                "visualizations": self._generate_session_visualizations(session)
            }
        except Exception as e:
            logger.error(f"Error generating session analysis: {str(e)}")
            return {"error": str(e)}

    def _summarize_alerts(
        self,
        alerts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Summarize alerts from session."""
        summary = {
            "total": len(alerts),
            "by_type": {},
            "by_severity": {},
            "affected_students": set()
        }
        
        for alert in alerts:
            # Count by type
            alert_type = alert["type"]
            summary["by_type"][alert_type] = summary["by_type"].get(alert_type, 0) + 1
            
            # Count by severity
            severity = alert["severity"]
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            
            # Track affected students
            if "affected_students" in alert:
                summary["affected_students"].update(alert["affected_students"])
        
        summary["affected_students"] = list(summary["affected_students"])
        return summary

    def _analyze_metric_trends(
        self,
        metrics_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze trends in metrics over time."""
        if not metrics_history:
            return {}

        trends = {}
        for metric in ["density", "transitivity", "average_clustering"]:
            values = [m[metric] for m in metrics_history]
            trends[metric] = {
                "start": values[0],
                "end": values[-1],
                "min": min(values),
                "max": max(values),
                "trend": np.polyfit(range(len(values)), values, 1)[0]
            }

        return trends

    def _generate_session_visualizations(
        self,
        session: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate visualizations for session analysis."""
        return {
            "interaction_timeline": self._create_interaction_timeline(session),
            "metric_trends": self._create_metric_trends(session["metrics_history"]),
            "alert_distribution": self._create_alert_distribution(session["alerts"]),
            "participation_heatmap": self._create_participation_heatmap(session)
        }

    def _create_interaction_timeline(
        self,
        session: Dict[str, Any]
    ) -> Dict[str, List[Any]]:
        """Create timeline of interactions."""
        timeline = []
        start_time = session["start_time"]
        
        for interaction in session["interaction_history"]:
            timestamp = interaction.get("timestamp", start_time)
            timeline.append({
                "time": (timestamp - start_time).seconds,
                "students": interaction["student_ids"],
                "type": interaction.get("type", "general"),
                "strength": interaction.get("strength", 1.0)
            })
            
        return timeline

    def _create_metric_trends(
        self,
        metrics_history: List[Dict[str, Any]]
    ) -> Dict[str, List[float]]:
        """Create visualization data for metric trends."""
        return {
            metric: [m[metric] for m in metrics_history]
            for metric in ["density", "transitivity", "average_clustering"]
        }

    def _create_alert_distribution(
        self,
        alerts: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, int]]:
        """Create visualization data for alert distribution."""
        distribution = {
            "by_type": {},
            "by_severity": {},
            "by_time": {}
        }
        
        for alert in alerts:
            alert_type = alert["type"]
            severity = alert["severity"]
            
            distribution["by_type"][alert_type] = distribution["by_type"].get(alert_type, 0) + 1
            distribution["by_severity"][severity] = distribution["by_severity"].get(severity, 0) + 1
            
        return distribution

    def _create_participation_heatmap(
        self,
        session: Dict[str, Any]
    ) -> List[List[float]]:
        """Create participation heatmap data."""
        n_students = len(session["group_data"]["students"])
        heatmap = np.zeros((n_students, n_students))
        
        for interaction in session["interaction_history"]:
            i, j = interaction["student_ids"]
            strength = interaction.get("strength", 1.0)
            heatmap[i][j] += strength
            heatmap[j][i] += strength
            
        return heatmap.tolist()

@lru_cache()
def get_ai_group_service() -> AIGroupAnalysis:
    """Get cached AI group analysis service instance."""
    return AIGroupAnalysis() 
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from fastapi import Depends

from app.services.physical_education.models.safety import EquipmentCheck
from app.core.database import get_db

class EquipmentManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.maintenance_statuses = [
            "good", "needs_inspection", "needs_repair",
            "needs_replacement", "out_of_service"
        ]
        self.damage_statuses = [
            "none", "minor", "moderate", "severe",
            "needs_repair", "needs_replacement"
        ]
        self.age_statuses = [
            "new", "good", "fair", "poor",
            "needs_replacement"
        ]

    async def create_equipment_check(
        self,
        class_id: str,
        equipment_id: str,
        maintenance_status: str,
        damage_status: str,
        age_status: str,
        last_maintenance: Optional[datetime] = None,
        purchase_date: Optional[datetime] = None,
        max_age_years: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Create a new equipment check record."""
        try:
            # Validate maintenance status
            if maintenance_status not in self.maintenance_statuses:
                raise ValueError(f"Invalid maintenance status. Must be one of: {self.maintenance_statuses}")
            
            # Validate damage status
            if damage_status not in self.damage_statuses:
                raise ValueError(f"Invalid damage status. Must be one of: {self.damage_statuses}")
            
            # Validate age status
            if age_status not in self.age_statuses:
                raise ValueError(f"Invalid age status. Must be one of: {self.age_statuses}")
            
            check = EquipmentCheck(
                class_id=class_id,
                equipment_id=equipment_id,
                check_date=datetime.utcnow(),
                maintenance_status=maintenance_status,
                damage_status=damage_status,
                age_status=age_status,
                last_maintenance=last_maintenance,
                purchase_date=purchase_date,
                max_age_years=max_age_years,
                metadata=metadata or {}
            )
            
            db.add(check)
            db.commit()
            db.refresh(check)
            
            return {
                "success": True,
                "message": "Equipment check created successfully",
                "check_id": check.id
            }
            
        except Exception as e:
            self.logger.error(f"Error creating equipment check: {str(e)}")
            if db:
                db.rollback()
            return {
                "success": False,
                "message": f"Error creating equipment check: {str(e)}"
            }

    async def get_equipment_check(
        self,
        check_id: str,
        db: Session = Depends(get_db)
    ) -> Optional[EquipmentCheck]:
        """Retrieve a specific equipment check by ID."""
        try:
            return db.query(EquipmentCheck).filter(EquipmentCheck.id == check_id).first()
        except Exception as e:
            self.logger.error(f"Error retrieving equipment check: {str(e)}")
            return None

    async def get_equipment_checks(
        self,
        class_id: Optional[str] = None,
        equipment_id: Optional[str] = None,
        maintenance_status: Optional[str] = None,
        damage_status: Optional[str] = None,
        age_status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_db)
    ) -> List[EquipmentCheck]:
        """Retrieve equipment checks with optional filters."""
        try:
            query = db.query(EquipmentCheck)
            
            if class_id:
                query = query.filter(EquipmentCheck.class_id == class_id)
            if equipment_id:
                query = query.filter(EquipmentCheck.equipment_id == equipment_id)
            if maintenance_status:
                query = query.filter(EquipmentCheck.maintenance_status == maintenance_status)
            if damage_status:
                query = query.filter(EquipmentCheck.damage_status == damage_status)
            if age_status:
                query = query.filter(EquipmentCheck.age_status == age_status)
            if start_date:
                query = query.filter(EquipmentCheck.check_date >= start_date)
            if end_date:
                query = query.filter(EquipmentCheck.check_date <= end_date)
            
            return query.all()
            
        except Exception as e:
            self.logger.error(f"Error retrieving equipment checks: {str(e)}")
            return []

    async def update_equipment_check(
        self,
        check_id: str,
        update_data: Dict[str, Any],
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Update an existing equipment check."""
        try:
            check = db.query(EquipmentCheck).filter(EquipmentCheck.id == check_id).first()
            if not check:
                return {
                    "success": False,
                    "message": "Equipment check not found"
                }
            
            # Validate and update fields
            for key, value in update_data.items():
                if hasattr(check, key):
                    if key == "maintenance_status" and value not in self.maintenance_statuses:
                        raise ValueError(f"Invalid maintenance status: {value}")
                    if key == "damage_status" and value not in self.damage_statuses:
                        raise ValueError(f"Invalid damage status: {value}")
                    if key == "age_status" and value not in self.age_statuses:
                        raise ValueError(f"Invalid age status: {value}")
                    setattr(check, key, value)
            
            db.commit()
            db.refresh(check)
            
            return {
                "success": True,
                "message": "Equipment check updated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error updating equipment check: {str(e)}")
            if db:
                db.rollback()
            return {
                "success": False,
                "message": f"Error updating equipment check: {str(e)}"
            }

    async def delete_equipment_check(
        self,
        check_id: str,
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Delete an equipment check."""
        try:
            check = db.query(EquipmentCheck).filter(EquipmentCheck.id == check_id).first()
            if not check:
                return {
                    "success": False,
                    "message": "Equipment check not found"
                }
            
            db.delete(check)
            db.commit()
            
            return {
                "success": True,
                "message": "Equipment check deleted successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting equipment check: {str(e)}")
            if db:
                db.rollback()
            return {
                "success": False,
                "message": f"Error deleting equipment check: {str(e)}"
            }

    async def get_equipment_statistics(
        self,
        class_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Get statistics about equipment checks."""
        try:
            query = db.query(EquipmentCheck)
            if class_id:
                query = query.filter(EquipmentCheck.class_id == class_id)
            if start_date:
                query = query.filter(EquipmentCheck.check_date >= start_date)
            if end_date:
                query = query.filter(EquipmentCheck.check_date <= end_date)
            
            checks = query.all()
            
            stats = {
                "total": len(checks),
                "by_equipment": {},
                "by_maintenance": {},
                "by_damage": {},
                "by_age": {},
                "trends": {}
            }
            
            for check in checks:
                # Count by equipment
                stats["by_equipment"][check.equipment_id] = \
                    stats["by_equipment"].get(check.equipment_id, {})
                stats["by_equipment"][check.equipment_id]["total"] = \
                    stats["by_equipment"][check.equipment_id].get("total", 0) + 1
                
                # Count by maintenance status
                stats["by_maintenance"][check.maintenance_status] = \
                    stats["by_maintenance"].get(check.maintenance_status, 0) + 1
                
                # Count by damage status
                stats["by_damage"][check.damage_status] = \
                    stats["by_damage"].get(check.damage_status, 0) + 1
                
                # Count by age status
                stats["by_age"][check.age_status] = \
                    stats["by_age"].get(check.age_status, 0) + 1
                
                # Calculate trends
                date_key = check.check_date.strftime("%Y-%m")
                stats["trends"][date_key] = stats["trends"].get(date_key, 0) + 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating equipment statistics: {str(e)}")
            return {}

    async def bulk_update_equipment_checks(
        self,
        updates: List[Dict[str, Any]],
        db: Session = Depends(get_db)
    ) -> Dict[str, int]:
        """Bulk update multiple equipment checks."""
        try:
            success_count = 0
            failure_count = 0
            
            for update in updates:
                try:
                    check_id = update.pop("id")
                    result = await self.update_equipment_check(check_id, update, db)
                    if result["success"]:
                        success_count += 1
                    else:
                        failure_count += 1
                except Exception as e:
                    self.logger.error(f"Error in bulk update: {str(e)}")
                    failure_count += 1
            
            return {
                "success": success_count,
                "failure": failure_count
            }
            
        except Exception as e:
            self.logger.error(f"Error in bulk update operation: {str(e)}")
            if db:
                db.rollback()
            return {
                "success": 0,
                "failure": len(updates)
            }

    async def bulk_delete_equipment_checks(
        self,
        check_ids: List[str],
        db: Session = Depends(get_db)
    ) -> Dict[str, int]:
        """Bulk delete multiple equipment checks."""
        try:
            success_count = 0
            failure_count = 0
            
            for check_id in check_ids:
                try:
                    result = await self.delete_equipment_check(check_id, db)
                    if result["success"]:
                        success_count += 1
                    else:
                        failure_count += 1
                except Exception as e:
                    self.logger.error(f"Error in bulk delete: {str(e)}")
                    failure_count += 1
            
            return {
                "success": success_count,
                "failure": failure_count
            }
            
        except Exception as e:
            self.logger.error(f"Error in bulk delete operation: {str(e)}")
            if db:
                db.rollback()
            return {
                "success": 0,
                "failure": len(check_ids)
            } 
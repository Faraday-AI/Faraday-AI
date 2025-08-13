"""Seed data for safety checks."""
from datetime import datetime, timedelta
import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.physical_education.safety.models import SafetyCheck

def seed_safety_checks(session):
    """Seed the safety_checks table with comprehensive and realistic safety data."""
    
    # First delete existing safety checks
    session.execute(SafetyCheck.__table__.delete())
    
    # Generate comprehensive safety check data
    safety_checks = [
        # EQUIPMENT SAFETY CHECKS
        {
            "check_type": "EQUIPMENT",
            "description": "Basketball hoop stability check - ensure hoops are securely mounted and nets are intact",
            "priority": "HIGH",
            "status": "COMPLETED",
            "assigned_to": "PE Teacher",
            "checked_by": 1,  # John Smith (teacher)
            "performed_by": 1,  # John Smith (teacher)
            "check_date": datetime.now() - timedelta(days=2),
            "due_date": datetime.now() + timedelta(days=7),
            "completed_date": datetime.now() - timedelta(days=2),
            "notes": "All hoops checked and secured, nets replaced on Court A",
            "location": "Basketball Court A",
            "equipment_involved": "Basketball hoops, nets",
            "risk_level": "MEDIUM"
        },
        {
            "check_type": "EQUIPMENT",
            "description": "Soccer goal post inspection - check for rust, stability, and proper anchoring",
            "priority": "HIGH",
            "status": "COMPLETED",
            "assigned_to": "PE Teacher",
            "checked_by": 2,  # Sarah Johnson (teacher)
            "performed_by": 2,  # Sarah Johnson (teacher)
            "check_date": datetime.now() - timedelta(days=1),
            "due_date": datetime.now() + timedelta(days=5),
            "completed_date": datetime.now() - timedelta(days=1),
            "notes": "Goals inspected, minor rust treatment applied, all anchors secure",
            "location": "Soccer Field",
            "equipment_involved": "Soccer goals, anchors",
            "risk_level": "MEDIUM"
        },
        {
            "check_type": "EQUIPMENT",
            "description": "Jump rope condition assessment - check for fraying, proper length, and handle integrity",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "assigned_to": "PE Teacher",
            "checked_by": 3,  # Michael Brown (teacher)
            "performed_by": 3,  # Michael Brown (teacher)
            "check_date": datetime.now() - timedelta(days=3),
            "due_date": datetime.now() + timedelta(days=14),
            "completed_date": datetime.now() - timedelta(days=3),
            "notes": "15 ropes replaced due to wear, all others in good condition",
            "location": "Equipment Room",
            "equipment_involved": "Jump ropes",
            "risk_level": "LOW"
        },
        {
            "check_type": "EQUIPMENT",
            "description": "Weight equipment safety inspection - check for loose bolts, worn cables, and stability",
            "priority": "HIGH",
            "status": "COMPLETED",
            "assigned_to": "PE Teacher",
            "checked_by": 1,  # John Smith (teacher)
            "performed_by": 1,  # John Smith (teacher)
            "check_date": datetime.now() - timedelta(days=1),
            "due_date": datetime.now() + timedelta(days=3),
            "completed_date": datetime.now() - timedelta(days=1),
            "notes": "All equipment inspected, cables replaced on machine #3",
            "location": "Weight Room",
            "equipment_involved": "Weight machines, cables, bolts",
            "risk_level": "HIGH"
        },
        {
            "check_type": "EQUIPMENT",
            "description": "Mats and padding inspection - check for tears, proper thickness, and placement",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "assigned_to": "PE Teacher",
            "checked_by": 2,  # Sarah Johnson (teacher)
            "performed_by": 2,  # Sarah Johnson (teacher)
            "check_date": datetime.now() - timedelta(days=2),
            "due_date": datetime.now() + timedelta(days=10),
            "completed_date": datetime.now() - timedelta(days=2),
            "notes": "2 mats replaced, all padding properly positioned",
            "location": "Gymnasium A",
            "equipment_involved": "Exercise mats, padding",
            "risk_level": "MEDIUM"
        },
        
        # FACILITY SAFETY CHECKS
        {
            "check_type": "FACILITY",
            "description": "Gymnasium floor inspection - check for loose boards, proper traction, and cleanliness",
            "priority": "HIGH",
            "status": "COMPLETED",
            "assigned_to": "Maintenance Staff",
            "checked_by": 1,  # John Smith (teacher) - acting as maintenance
            "performed_by": 1,  # John Smith (teacher) - acting as maintenance
            "check_date": datetime.now() - timedelta(days=1),
            "due_date": datetime.now() + timedelta(days=7),
            "completed_date": datetime.now() - timedelta(days=1),
            "notes": "Floor cleaned and inspected, minor repairs completed",
            "location": "Gymnasium A",
            "equipment_involved": "Flooring, cleaning equipment",
            "risk_level": "MEDIUM"
        },
        {
            "check_type": "FACILITY",
            "description": "Emergency exit accessibility check - ensure all exits are clear and properly marked",
            "priority": "CRITICAL",
            "status": "COMPLETED",
            "assigned_to": "Safety Officer",
            "checked_by": 2,  # Sarah Johnson (teacher) - acting as safety officer
            "performed_by": 2,  # Sarah Johnson (teacher) - acting as safety officer
            "check_date": datetime.now() - timedelta(hours=6),
            "due_date": datetime.now() + timedelta(days=1),
            "completed_date": datetime.now() - timedelta(hours=6),
            "notes": "All exits clear, signage updated, emergency lighting tested",
            "location": "All Facilities",
            "equipment_involved": "Exit signs, emergency lighting",
            "risk_level": "CRITICAL"
        },
        {
            "check_type": "FACILITY",
            "description": "First aid kit inventory and expiration check - ensure all supplies are current and complete",
            "priority": "HIGH",
            "status": "COMPLETED",
            "assigned_to": "School Nurse",
            "checked_by": 3,  # Michael Brown (teacher) - acting as school nurse
            "performed_by": 3,  # Michael Brown (teacher) - acting as school nurse
            "check_date": datetime.now() - timedelta(days=1),
            "due_date": datetime.now() + timedelta(days=5),
            "completed_date": datetime.now() - timedelta(days=1),
            "notes": "All kits restocked, expired items replaced, inventory updated",
            "location": "All PE Locations",
            "equipment_involved": "First aid kits, medical supplies",
            "risk_level": "HIGH"
        },
        {
            "check_type": "FACILITY",
            "description": "Lighting system inspection - check for proper illumination and emergency backup",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "assigned_to": "Maintenance Staff",
            "checked_by": 2,  # Sarah Johnson (teacher) - acting as maintenance
            "performed_by": 2,  # Sarah Johnson (teacher) - acting as maintenance
            "check_date": datetime.now() - timedelta(days=2),
            "due_date": datetime.now() + timedelta(days=14),
            "completed_date": datetime.now() - timedelta(days=2),
            "notes": "All lights functioning, emergency backup tested",
            "location": "All Facilities",
            "equipment_involved": "Lighting fixtures, emergency backup",
            "risk_level": "LOW"
        },
        {
            "check_type": "FACILITY",
            "description": "Ventilation system check - ensure proper air circulation and temperature control",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "assigned_to": "Maintenance Staff",
            "checked_by": 1,  # John Smith (teacher) - acting as maintenance
            "performed_by": 1,  # John Smith (teacher) - acting as maintenance
            "check_date": datetime.now() - timedelta(days=3),
            "due_date": datetime.now() + timedelta(days=21),
            "completed_date": datetime.now() - timedelta(days=3),
            "notes": "Ventilation working properly, filters changed",
            "location": "All Facilities",
            "equipment_involved": "HVAC system, filters",
            "risk_level": "LOW"
        },
        
        # ENVIRONMENTAL SAFETY CHECKS
        {
            "check_type": "ENVIRONMENTAL",
            "description": "Weather condition assessment for outdoor activities - check temperature, precipitation, and wind",
            "priority": "HIGH",
            "status": "COMPLETED",
            "assigned_to": "PE Teacher",
            "checked_by": 3,  # Michael Brown (teacher)
            "performed_by": 3,  # Michael Brown (teacher)
            "check_date": datetime.now() - timedelta(hours=2),
            "due_date": datetime.now() + timedelta(days=1),
            "completed_date": datetime.now() - timedelta(hours=2),
            "notes": "Weather suitable for outdoor activities, no extreme conditions",
            "location": "Outdoor Facilities",
            "equipment_involved": "Weather monitoring equipment",
            "risk_level": "MEDIUM"
        },
        {
            "check_type": "ENVIRONMENTAL",
            "description": "Surface condition check for outdoor fields - assess for wetness, ice, and debris",
            "priority": "HIGH",
            "status": "COMPLETED",
            "assigned_to": "PE Teacher",
            "checked_by": 1,  # John Smith (teacher)
            "performed_by": 1,  # John Smith (teacher)
            "check_date": datetime.now() - timedelta(hours=3),
            "due_date": datetime.now() + timedelta(days=1),
            "completed_date": datetime.now() - timedelta(hours=3),
            "notes": "Fields dry and clear, no safety hazards detected",
            "location": "Soccer Field, Track",
            "equipment_involved": "Field maintenance equipment",
            "risk_level": "MEDIUM"
        },
        {
            "check_type": "ENVIRONMENTAL",
            "description": "Air quality assessment for indoor activities - check for proper ventilation and air quality",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "assigned_to": "Maintenance Staff",
            "checked_by": 2,  # Sarah Johnson (teacher) - acting as maintenance
            "performed_by": 2,  # Sarah Johnson (teacher) - acting as maintenance
            "check_date": datetime.now() - timedelta(days=1),
            "due_date": datetime.now() + timedelta(days=7),
            "completed_date": datetime.now() - timedelta(days=1),
            "notes": "Air quality good, ventilation systems functioning properly",
            "location": "Indoor Facilities",
            "equipment_involved": "Air quality monitors",
            "risk_level": "LOW"
        },
        {
            "check_type": "ENVIRONMENTAL",
            "description": "Temperature and humidity monitoring for optimal activity conditions",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "assigned_to": "PE Teacher",
            "checked_by": 3,  # Michael Brown (teacher)
            "performed_by": 3,  # Michael Brown (teacher)
            "check_date": datetime.now() - timedelta(hours=4),
            "due_date": datetime.now() + timedelta(days=1),
            "completed_date": datetime.now() - timedelta(hours=4),
            "notes": "Temperature 72°F, humidity 45% - optimal conditions",
            "location": "Indoor Facilities",
            "equipment_involved": "Thermometers, hygrometers",
            "risk_level": "LOW"
        },
        
        # PROCEDURAL SAFETY CHECKS
        {
            "check_type": "PROCEDURAL",
            "description": "Emergency response plan review and update - ensure all procedures are current",
            "priority": "CRITICAL",
            "status": "COMPLETED",
            "assigned_to": "Safety Officer",
            "checked_by": 1,  # John Smith (teacher) - acting as safety officer
            "performed_by": 1,  # John Smith (teacher) - acting as safety officer
            "check_date": datetime.now() - timedelta(days=5),
            "due_date": datetime.now() + timedelta(days=30),
            "completed_date": datetime.now() - timedelta(days=5),
            "notes": "Plan updated, staff trained on new procedures",
            "location": "All Facilities",
            "equipment_involved": "Emergency response documentation",
            "risk_level": "CRITICAL"
        },
        {
            "check_type": "PROCEDURAL",
            "description": "Student medical information verification - check for updated health records and restrictions",
            "priority": "HIGH",
            "status": "COMPLETED",
            "assigned_to": "School Nurse",
            "checked_by": 2,  # Sarah Johnson (teacher) - acting as school nurse
            "performed_by": 2,  # Sarah Johnson (teacher) - acting as school nurse
            "check_date": datetime.now() - timedelta(days=2),
            "due_date": datetime.now() + timedelta(days=14),
            "completed_date": datetime.now() - timedelta(days=2),
            "notes": "All records updated, new restrictions noted for 3 students",
            "location": "All PE Classes",
            "equipment_involved": "Medical records, health forms",
            "risk_level": "HIGH"
        },
        {
            "check_type": "PROCEDURAL",
            "description": "Staff safety training verification - ensure all PE staff have current certifications",
            "priority": "HIGH",
            "status": "COMPLETED",
            "assigned_to": "PE Department Head",
            "checked_by": 3,  # Michael Brown (teacher) - acting as department head
            "performed_by": 3,  # Michael Brown (teacher) - acting as department head
            "check_date": datetime.now() - timedelta(days=1),
            "due_date": datetime.now() + timedelta(days=21),
            "completed_date": datetime.now() - timedelta(days=1),
            "notes": "All staff certified, 2 staff members completed refresher training",
            "location": "All Facilities",
            "equipment_involved": "Training records, certifications",
            "risk_level": "HIGH"
        },
        {
            "check_type": "PROCEDURAL",
            "description": "Activity-specific safety protocols review - update safety guidelines for each activity",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "assigned_to": "PE Teacher",
            "checked_by": 1,  # John Smith (teacher)
            "performed_by": 1,  # John Smith (teacher)
            "check_date": datetime.now() - timedelta(days=3),
            "due_date": datetime.now() + timedelta(days=30),
            "completed_date": datetime.now() - timedelta(days=3),
            "notes": "All protocols reviewed and updated, new guidelines distributed",
            "location": "All Facilities",
            "equipment_involved": "Safety protocol documentation",
            "risk_level": "MEDIUM"
        },
        {
            "check_type": "PROCEDURAL",
            "description": "Incident reporting system check - verify reporting procedures and contact information",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "assigned_to": "Administrative Staff",
            "checked_by": 2,  # Sarah Johnson (teacher) - acting as administrative staff
            "performed_by": 2,  # Sarah Johnson (teacher) - acting as administrative staff
            "check_date": datetime.now() - timedelta(days=1),
            "due_date": datetime.now() + timedelta(days=14),
            "completed_date": datetime.now() - timedelta(days=1),
            "notes": "System tested, all contact information verified and updated",
            "location": "All Facilities",
            "equipment_involved": "Reporting system, contact lists",
            "risk_level": "MEDIUM"
        },
        
        # SCHEDULED MAINTENANCE CHECKS
        {
            "check_type": "MAINTENANCE",
            "description": "Monthly equipment deep cleaning and sanitization",
            "priority": "MEDIUM",
            "status": "COMPLETED",
            "assigned_to": "Maintenance Staff",
            "checked_by": 3,  # Michael Brown (teacher) - acting as maintenance
            "performed_by": 3,  # Michael Brown (teacher) - acting as maintenance
            "check_date": datetime.now() - timedelta(days=2),
            "due_date": datetime.now() + timedelta(days=30),
            "completed_date": datetime.now() - timedelta(days=2),
            "notes": "All equipment cleaned and sanitized, storage areas organized",
            "location": "Equipment Room",
            "equipment_involved": "Cleaning supplies, sanitizers",
            "risk_level": "LOW"
        },
        {
            "check_type": "MAINTENANCE",
            "description": "Quarterly facility safety audit - comprehensive review of all safety systems",
            "priority": "HIGH",
            "status": "COMPLETED",
            "assigned_to": "Safety Officer",
            "checked_by": 1,  # John Smith (teacher) - acting as safety officer
            "performed_by": 1,  # John Smith (teacher) - acting as safety officer
            "check_date": datetime.now() - timedelta(days=7),
            "due_date": datetime.now() + timedelta(days=90),
            "completed_date": datetime.now() - timedelta(days=7),
            "notes": "Full audit completed, minor issues addressed, major systems functioning",
            "location": "All Facilities",
            "equipment_involved": "Safety audit checklist",
            "risk_level": "MEDIUM"
        }
    ]

    # Create and add safety checks
    for check_data in safety_checks:
        safety_check = SafetyCheck(**check_data)
        session.add(safety_check)

    session.commit()
    
    # Verify safety checks were created
    result = session.execute(text("SELECT COUNT(*) FROM safety_checks"))
    count = result.scalar()
    print(f"Seeded {count} safety checks. Total safety checks in database: {count}")
    
    # Print safety checks by type
    result = session.execute(text("SELECT check_type, priority, status, COUNT(*) as count FROM safety_checks GROUP BY check_type, priority, status ORDER BY check_type, priority"))
    type_summary = result.fetchall()
    
    print("\nSafety checks by type and priority:")
    current_type = None
    for row in type_summary:
        if row.check_type != current_type:
            current_type = row.check_type
            print(f"\n{current_type}:")
        print(f"  {row.priority} priority - {row.status}: {row.count} checks")
    
    # Print sample of recent safety checks
    result = session.execute(text("SELECT check_type, description, priority, status FROM safety_checks ORDER BY completed_date DESC LIMIT 5"))
    recent_checks = result.fetchall()
    
    print("\nRecent safety checks completed:")
    for check in recent_checks:
        print(f"  - {check.check_type}: {check.description[:60]}... ({check.priority} priority, {check.status})") 
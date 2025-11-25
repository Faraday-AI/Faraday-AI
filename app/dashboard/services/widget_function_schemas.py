"""
Widget Function Schemas

GPT function schemas for controlling Physical Education, Health, and Drivers Ed widgets
through natural language commands via the AI Avatar.
"""

from typing import Dict, List, Any


class WidgetFunctionSchemas:
    """GPT function schemas for widget control."""
    
    # ==================== PHYSICAL EDUCATION WIDGETS ====================
    
    @staticmethod
    def get_physical_education_schemas() -> List[Dict[str, Any]]:
        """Get all Physical Education widget function schemas."""
        return [
            # Attendance Tracker Widget
            {
                "name": "get_attendance_patterns",
                "description": "Get attendance patterns and predictions for a PE class. Can identify at-risk students and predict future attendance. Admin users can query any teacher's classes by providing teacher_id, teacher_name, or teacher_email.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_id": {
                            "type": "integer",
                            "description": "Physical education class ID"
                        },
                        "period": {
                            "type": "string",
                            "description": "Optional class period (e.g., 'Period 2', 'fourth period'). Admin users can query any teacher's period."
                        },
                        "student_id": {
                            "type": "integer",
                            "description": "Optional specific student ID to analyze"
                        },
                        "days_ahead": {
                            "type": "integer",
                            "description": "Number of days to predict ahead (default: 7)",
                            "default": 7
                        },
                        "teacher_id": {
                            "type": "integer",
                            "description": "Optional teacher ID (admin only - allows querying any teacher's classes)"
                        },
                        "teacher_name": {
                            "type": "string",
                            "description": "Optional teacher name (admin only - allows querying any teacher's classes by name)"
                        },
                        "teacher_email": {
                            "type": "string",
                            "description": "Optional teacher email (admin only - allows querying any teacher's classes by email)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "mark_attendance",
                "description": "Mark attendance for students in a PE class on a specific date. Admin users can mark attendance for any teacher's classes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_id": {
                            "type": "integer",
                            "description": "Physical education class ID"
                        },
                        "period": {
                            "type": "string",
                            "description": "Optional class period (e.g., 'Period 2', 'fourth period'). Admin users can query any teacher's period."
                        },
                        "date": {
                            "type": "string",
                            "description": "Date in YYYY-MM-DD format (default: today)"
                        },
                        "attendance_records": {
                            "type": "array",
                            "description": "Array of attendance records",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "student_id": {"type": "integer"},
                                    "status": {
                                        "type": "string",
                                        "enum": ["present", "absent", "late", "excused"]
                                    },
                                    "participation_level": {
                                        "type": "string",
                                        "enum": ["excellent", "good", "fair", "poor"],
                                        "description": "Optional participation rating"
                                    },
                                    "notes": {"type": "string"}
                                },
                                "required": ["student_id", "status"]
                            }
                        },
                        "teacher_id": {
                            "type": "integer",
                            "description": "Optional teacher ID (admin only - allows marking attendance for any teacher's classes)"
                        },
                        "teacher_name": {
                            "type": "string",
                            "description": "Optional teacher name (admin only - allows marking attendance for any teacher's classes by name)"
                        },
                        "teacher_email": {
                            "type": "string",
                            "description": "Optional teacher email (admin only - allows marking attendance for any teacher's classes by email)"
                        }
                    },
                    "required": ["attendance_records"]
                }
            },
            
            # Team Generator Widget
            {
                "name": "create_teams",
                "description": "Create teams and squads for a PE class. Can handle complex configurations like 'red team and blue team with five squads each'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_id": {
                            "type": "integer",
                            "description": "Physical education class ID"
                        },
                        "period": {
                            "type": "string",
                            "description": "Optional class period (e.g., 'fourth period', 'Period 4')"
                        },
                        "team_config": {
                            "type": "object",
                            "description": "Team configuration",
                            "properties": {
                                "team_count": {
                                    "type": "integer",
                                    "description": "Number of teams to create"
                                },
                                "team_names": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Optional custom team names (e.g., ['Red Team', 'Blue Team'])"
                                },
                                "team_colors": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Optional team colors"
                                },
                                "squad_count": {
                                    "type": "integer",
                                    "description": "Number of squads per team (0 = no squads)",
                                    "default": 0
                                },
                                "balance_by": {
                                    "type": "string",
                                    "enum": ["skill", "random", "size"],
                                    "description": "How to balance teams",
                                    "default": "random"
                                }
                            },
                            "required": ["team_count"]
                        },
                        "activity_type": {
                            "type": "string",
                            "description": "Type of activity (e.g., 'basketball', 'soccer')"
                        }
                    },
                    "required": ["class_id", "team_config"]
                }
            },
            {
                "name": "get_class_roster",
                "description": "Get the roster of students for a specific class period (e.g., 'fourth period class'). Admin users can query any teacher's classes by providing teacher_id, teacher_name, or teacher_email.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_id": {
                            "type": "integer",
                            "description": "Physical education class ID (optional if period provided)"
                        },
                        "period": {
                            "type": "string",
                            "description": "Class period (e.g., 'fourth period', 'Period 4', '4th period'). Admin users can query any teacher's period."
                        },
                        "teacher_id": {
                            "type": "integer",
                            "description": "Optional teacher ID (admin only - allows querying any teacher's classes)"
                        },
                        "teacher_name": {
                            "type": "string",
                            "description": "Optional teacher name (admin only - allows querying any teacher's classes by name)"
                        },
                        "teacher_email": {
                            "type": "string",
                            "description": "Optional teacher email (admin only - allows querying any teacher's classes by email)"
                        }
                    },
                    "required": []
                }
            },
            
            # Adaptive PE Widget
            {
                "name": "suggest_adaptive_accommodations",
                "description": "Suggest adaptive accommodations for a student with special needs based on activity type and medical notes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "integer",
                            "description": "Student ID"
                        },
                        "activity_type": {
                            "type": "string",
                            "description": "Type of activity (e.g., 'basketball', 'running')"
                        },
                        "medical_notes": {
                            "type": "string",
                            "description": "Optional medical notes or IEP information"
                        }
                    },
                    "required": ["student_id", "activity_type"]
                }
            },
            {
                "name": "create_adaptive_activity",
                "description": "Create an adaptive activity for a student with modifications and accommodations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "integer",
                            "description": "Student ID"
                        },
                        "activity_name": {
                            "type": "string",
                            "description": "Name of the activity"
                        },
                        "base_activity_id": {
                            "type": "integer",
                            "description": "Optional base activity ID to adapt from"
                        },
                        "modifications": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of modifications to apply"
                        },
                        "equipment": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Required equipment list"
                        },
                        "safety_notes": {
                            "type": "string",
                            "description": "Safety considerations"
                        },
                        "difficulty_level": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Difficulty level"
                        }
                    },
                    "required": ["student_id", "activity_name"]
                }
            },
            
            # Progress Analytics Widget
            {
                "name": "predict_student_performance",
                "description": "Predict student performance based on historical data. Can forecast performance trends and suggest interventions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "integer",
                            "description": "Student ID"
                        },
                        "activity_id": {
                            "type": "integer",
                            "description": "Optional specific activity ID"
                        },
                        "weeks_ahead": {
                            "type": "integer",
                            "description": "Number of weeks to predict ahead (default: 4)",
                            "default": 4
                        }
                    },
                    "required": ["student_id"]
                }
            },
            
            # Safety & Risk Assessment
            {
                "name": "identify_safety_risks",
                "description": "Identify potential safety risks for a class or activity. Provides recommendations for risk mitigation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_id": {
                            "type": "integer",
                            "description": "Physical education class ID"
                        },
                        "activity_id": {
                            "type": "integer",
                            "description": "Optional specific activity ID"
                        }
                    },
                    "required": ["class_id"]
                }
            },
            
            # Comprehensive Insights
            {
                "name": "get_class_insights",
                "description": "Get comprehensive insights for a class by combining attendance, performance, and health data from multiple widgets.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_id": {
                            "type": "integer",
                            "description": "Physical education class ID"
                        },
                        "include_attendance": {
                            "type": "boolean",
                            "description": "Include attendance data (default: true)",
                            "default": True
                        },
                        "include_performance": {
                            "type": "boolean",
                            "description": "Include performance data (default: true)",
                            "default": True
                        },
                        "include_health": {
                            "type": "boolean",
                            "description": "Include health metrics (default: true)",
                            "default": True
                        }
                    },
                    "required": ["class_id"]
                }
            }
        ]
    
    # ==================== HEALTH WIDGETS ====================
    
    @staticmethod
    def get_health_schemas() -> List[Dict[str, Any]]:
        """Get all Health widget function schemas."""
        return [
            {
                "name": "analyze_health_trends",
                "description": "Analyze health metric trends for students. Identifies patterns and potential health concerns.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "integer",
                            "description": "Student ID"
                        },
                        "metric_type": {
                            "type": "string",
                            "description": "Type of health metric (e.g., 'heart_rate', 'blood_pressure', 'weight')"
                        },
                        "time_range": {
                            "type": "string",
                            "enum": ["week", "month", "semester", "year"],
                            "description": "Time range for analysis",
                            "default": "month"
                        }
                    },
                    "required": ["student_id"]
                }
            },
            {
                "name": "identify_health_risks",
                "description": "Identify potential health risks for students based on health metrics and patterns.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_id": {
                            "type": "integer",
                            "description": "Physical education class ID"
                        },
                        "student_id": {
                            "type": "integer",
                            "description": "Optional specific student ID"
                        },
                        "risk_threshold": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Minimum risk level to report",
                            "default": "medium"
                        }
                    },
                    "required": ["class_id"]
                }
            },
            {
                "name": "generate_health_recommendations",
                "description": "Generate health recommendations for students based on their health metrics and activity participation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "integer",
                            "description": "Student ID"
                        },
                        "focus_area": {
                            "type": "string",
                            "enum": ["fitness", "nutrition", "wellness", "general"],
                            "description": "Focus area for recommendations",
                            "default": "general"
                        }
                    },
                    "required": ["student_id"]
                }
            }
        ]
    
    # ==================== DRIVERS ED WIDGETS ====================
    
    @staticmethod
    def get_drivers_ed_schemas() -> List[Dict[str, Any]]:
        """Get all Drivers Ed widget function schemas."""
        return [
            {
                "name": "create_drivers_ed_lesson_plan",
                "description": "Create a lesson plan for Drivers Ed class covering specific topics and activities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Lesson plan title"
                        },
                        "topic": {
                            "type": "string",
                            "description": "Lesson topic (e.g., 'defensive driving', 'parking', 'highway safety')"
                        },
                        "objectives": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Learning objectives"
                        },
                        "activities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "duration": {"type": "integer", "description": "Duration in minutes"}
                                }
                            }
                        },
                        "standards": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Standards alignment"
                        }
                    },
                    "required": ["title", "topic"]
                }
            },
            {
                "name": "track_student_driving_progress",
                "description": "Track student driving hours, skill development, and test scores for Drivers Ed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "integer",
                            "description": "Student ID"
                        },
                        "driving_hours": {
                            "type": "number",
                            "description": "Driving hours to add"
                        },
                        "skill_assessment": {
                            "type": "object",
                            "description": "Skill assessment data",
                            "properties": {
                                "skill": {"type": "string"},
                                "score": {"type": "number"},
                                "notes": {"type": "string"}
                            }
                        },
                        "test_score": {
                            "type": "number",
                            "description": "Test score to record"
                        }
                    },
                    "required": ["student_id"]
                }
            },
            {
                "name": "record_safety_incident",
                "description": "Record a safety incident in Drivers Ed class.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_id": {
                            "type": "integer",
                            "description": "Drivers Ed class ID"
                        },
                        "student_id": {
                            "type": "integer",
                            "description": "Student ID involved"
                        },
                        "incident_type": {
                            "type": "string",
                            "enum": ["minor", "moderate", "serious"],
                            "description": "Severity of incident"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the incident"
                        },
                        "date": {
                            "type": "string",
                            "description": "Date in YYYY-MM-DD format (default: today)"
                        }
                    },
                    "required": ["class_id", "incident_type", "description"]
                }
            },
            {
                "name": "manage_vehicle",
                "description": "Manage vehicle inventory, maintenance, and usage tracking for Drivers Ed program.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["add", "update", "schedule_maintenance", "record_usage", "check_status"],
                            "description": "Action to perform"
                        },
                        "vehicle_id": {
                            "type": "integer",
                            "description": "Vehicle ID (required for most actions)"
                        },
                        "vehicle_data": {
                            "type": "object",
                            "description": "Vehicle information",
                            "properties": {
                                "make": {"type": "string"},
                                "model": {"type": "string"},
                                "year": {"type": "integer"},
                                "license_plate": {"type": "string"},
                                "mileage": {"type": "integer"}
                            }
                        },
                        "maintenance_type": {
                            "type": "string",
                            "description": "Type of maintenance (for schedule_maintenance)"
                        },
                        "maintenance_date": {
                            "type": "string",
                            "description": "Scheduled maintenance date (YYYY-MM-DD)"
                        }
                    },
                    "required": ["action"]
                }
            }
        ]
    
    # ==================== WIDGET MANAGEMENT ====================
    
    @staticmethod
    def get_widget_management_schemas() -> List[Dict[str, Any]]:
        """Get widget management function schemas."""
        return [
            {
                "name": "create_widget",
                "description": "Create a new dashboard widget for Physical Education, Health, or Drivers Ed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "widget_type": {
                            "type": "string",
                            "description": "Type of widget (e.g., 'attendance_tracker', 'team_generator', 'health_metrics')"
                        },
                        "name": {
                            "type": "string",
                            "description": "Widget name"
                        },
                        "configuration": {
                            "type": "object",
                            "description": "Widget configuration"
                        },
                        "dashboard_id": {
                            "type": "integer",
                            "description": "Dashboard ID to add widget to"
                        }
                    },
                    "required": ["widget_type", "name", "dashboard_id"]
                }
            },
            {
                "name": "update_widget_configuration",
                "description": "Update the configuration of an existing widget.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "widget_id": {
                            "type": "integer",
                            "description": "Widget ID"
                        },
                        "configuration": {
                            "type": "object",
                            "description": "Updated widget configuration"
                        }
                    },
                    "required": ["widget_id", "configuration"]
                }
            },
            {
                "name": "get_widget_data",
                "description": "Get data from a specific widget.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "widget_id": {
                            "type": "integer",
                            "description": "Widget ID"
                        },
                        "refresh": {
                            "type": "boolean",
                            "description": "Force refresh of widget data",
                            "default": False
                        }
                    },
                    "required": ["widget_id"]
                }
            }
        ]
    
    @staticmethod
    def get_enhancement_schemas() -> List[Dict[str, Any]]:
        """Get schemas for all 21 enhancement features."""
        return [
            # Enhancement 2: Advanced Performance Prediction
            {
                "name": "predict_student_performance_advanced",
                "description": "Advanced performance prediction using ML-based forecasting with multiple factors (health, attendance, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {"type": "integer", "description": "Student ID"},
                        "activity_id": {"type": "integer", "description": "Optional specific activity ID"},
                        "weeks_ahead": {"type": "integer", "description": "Number of weeks to predict ahead", "default": 4},
                        "include_health_factors": {"type": "boolean", "description": "Include health metrics in prediction", "default": True},
                        "include_attendance_factors": {"type": "boolean", "description": "Include attendance patterns in prediction", "default": True}
                    },
                    "required": ["student_id"]
                }
            },
            # Enhancement 3: Automated Reporting & Communication
            {
                "name": "generate_automated_report",
                "description": "Generate automated reports (progress, attendance, health, comprehensive)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "report_type": {
                            "type": "string",
                            "enum": ["progress", "attendance", "health", "comprehensive"],
                            "description": "Type of report to generate"
                        },
                        "student_id": {"type": "integer", "description": "Optional student ID for individual reports"},
                        "class_id": {"type": "integer", "description": "Optional class ID for class reports"},
                        "time_range": {
                            "type": "string",
                            "enum": ["week", "month", "semester", "year"],
                            "description": "Time range for report",
                            "default": "month"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["text", "html", "json", "pdf"],
                            "description": "Report format",
                            "default": "text"
                        }
                    },
                    "required": ["report_type"]
                }
            },
            {
                "name": "send_automated_notification",
                "description": "Send automated notifications via email, SMS, or in-app",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "notification_type": {
                            "type": "string",
                            "enum": ["attendance_alert", "performance_update", "health_concern", "achievement", "reminder"],
                            "description": "Type of notification"
                        },
                        "recipient_id": {"type": "integer", "description": "ID of recipient (student_id or parent_id)"},
                        "recipient_type": {
                            "type": "string",
                            "enum": ["student", "parent", "teacher"],
                            "description": "Type of recipient",
                            "default": "student"
                        },
                        "message": {"type": "string", "description": "Optional custom message"},
                        "channel": {
                            "type": "string",
                            "enum": ["email", "sms", "in_app"],
                            "description": "Notification channel",
                            "default": "email"
                        }
                    },
                    "required": ["notification_type", "recipient_id"]
                }
            },
            # Enhancement 4: Workflow Automation
            {
                "name": "execute_workflow",
                "description": "Execute automated workflows (prepare_for_class, end_of_semester, safety_incident, daily_attendance_reminder)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "workflow_name": {
                            "type": "string",
                            "enum": ["prepare_for_class", "end_of_semester", "safety_incident", "daily_attendance_reminder"],
                            "description": "Name of workflow to execute"
                        },
                        "class_id": {"type": "integer", "description": "Optional class ID"},
                        "parameters": {"type": "object", "description": "Optional workflow parameters"}
                    },
                    "required": ["workflow_name"]
                }
            },
            # Enhancement 5: Cross-Widget Intelligence
            {
                "name": "analyze_cross_widget_correlations",
                "description": "Analyze correlations across different data sources (attendance, performance, health)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_id": {"type": "integer", "description": "Optional class ID"},
                        "student_id": {"type": "integer", "description": "Optional student ID"},
                        "time_range": {
                            "type": "string",
                            "enum": ["week", "month", "semester", "year"],
                            "description": "Time range for analysis",
                            "default": "month"
                        }
                    }
                }
            },
            # Enhancement 6: Anomaly Detection & Alerting
            {
                "name": "detect_anomalies",
                "description": "Detect anomalies in student data (performance, attendance, health)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_id": {"type": "integer", "description": "Optional class ID"},
                        "student_id": {"type": "integer", "description": "Optional student ID"},
                        "data_type": {
                            "type": "string",
                            "enum": ["performance", "attendance", "health"],
                            "description": "Type of data to analyze",
                            "default": "performance"
                        }
                    }
                }
            },
            {
                "name": "create_smart_alert",
                "description": "Create smart alerts that trigger based on conditions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "alert_type": {
                            "type": "string",
                            "enum": ["performance_drop", "attendance_drop", "health_concern", "safety_incident"],
                            "description": "Type of alert"
                        },
                        "student_id": {"type": "integer", "description": "Optional student ID"},
                        "class_id": {"type": "integer", "description": "Optional class ID"},
                        "threshold": {"type": "number", "description": "Optional threshold value"},
                        "conditions": {"type": "object", "description": "Optional alert conditions"}
                    },
                    "required": ["alert_type"]
                }
            },
            # Enhancement 7: Student Self-Service Portal
            {
                "name": "get_student_dashboard_data",
                "description": "Get comprehensive dashboard data for student self-service portal",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {"type": "integer", "description": "Student ID"},
                        "include_goals": {"type": "boolean", "description": "Include fitness goals", "default": True},
                        "include_progress": {"type": "boolean", "description": "Include progress tracking", "default": True}
                    },
                    "required": ["student_id"]
                }
            },
            {
                "name": "create_student_self_assessment",
                "description": "Create a student self-assessment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {"type": "integer", "description": "Student ID"},
                        "assessment_data": {
                            "type": "object",
                            "description": "Self-assessment data",
                            "properties": {
                                "assessment_type": {"type": "string"},
                                "responses": {"type": "object"},
                                "self_rating": {"type": "number"},
                                "reflection": {"type": "string"}
                            }
                        }
                    },
                    "required": ["student_id", "assessment_data"]
                }
            },
            # Enhancement 8: Advanced Equipment Management
            {
                "name": "predict_equipment_failure",
                "description": "Predict equipment failure using ML-based analysis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "equipment_id": {"type": "integer", "description": "Optional equipment ID"},
                        "equipment_name": {"type": "string", "description": "Optional equipment name"},
                        "time_horizon": {"type": "integer", "description": "Days ahead to predict", "default": 30}
                    }
                }
            },
            {
                "name": "optimize_equipment_inventory",
                "description": "Optimize equipment inventory levels",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_id": {"type": "integer", "description": "Optional class ID"},
                        "activity_type": {"type": "string", "description": "Optional activity type"}
                    }
                }
            },
            # Communication Functions with Translation
            {
                "name": "send_parent_message",
                "description": "Send message to parent via email and/or SMS with automatic translation. Supports multilingual communication.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {"type": "integer", "description": "Student ID"},
                        "message": {"type": "string", "description": "Message content to send"},
                        "message_type": {
                            "type": "string",
                            "enum": ["progress_update", "attendance_concern", "achievement", "general"],
                            "description": "Type of message",
                            "default": "progress_update"
                        },
                        "channels": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["email", "sms", "both"]},
                            "description": "Communication channels to use",
                            "default": ["email"]
                        },
                        "target_language": {
                            "type": "string",
                            "description": "Target language code (e.g., 'es' for Spanish). Auto-detected if not provided."
                        },
                        "auto_translate": {
                            "type": "boolean",
                            "description": "Automatically detect and translate message",
                            "default": True
                        }
                    },
                    "required": ["student_id", "message"]
                }
            },
            {
                "name": "send_student_message",
                "description": "Send message to student via email and/or SMS with automatic translation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {"type": "integer", "description": "Student ID"},
                        "message": {"type": "string", "description": "Message content"},
                        "channels": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["email", "sms", "both"]},
                            "description": "Communication channels",
                            "default": ["email"]
                        },
                        "target_language": {
                            "type": "string",
                            "description": "Target language code. Auto-detected if not provided."
                        },
                        "auto_translate": {
                            "type": "boolean",
                            "description": "Automatically detect and translate",
                            "default": True
                        }
                    },
                    "required": ["student_id", "message"]
                }
            },
            {
                "name": "send_teacher_message",
                "description": "Send message to another teacher via email with optional translation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient_teacher_id": {"type": "integer", "description": "Recipient teacher user ID"},
                        "message": {"type": "string", "description": "Message content"},
                        "channels": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["email", "sms", "both"]},
                            "description": "Communication channels",
                            "default": ["email"]
                        },
                        "target_language": {"type": "string", "description": "Target language code"}
                    },
                    "required": ["recipient_teacher_id", "message"]
                }
            },
            {
                "name": "send_administrator_message",
                "description": "Send message to administrators via email.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Message content"},
                        "admin_emails": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of admin emails. Auto-finds all admins if not provided."
                        },
                        "channels": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["email", "sms", "both"]},
                            "description": "Communication channels",
                            "default": ["email"]
                        }
                    },
                    "required": ["message"]
                }
            },
            {
                "name": "send_assignment_to_students",
                "description": "Send assignment to students via email with automatic translation. Each student receives assignment in their preferred language.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "assignment_id": {"type": "integer", "description": "Assignment ID"},
                        "student_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "List of student IDs to send assignment to"
                        },
                        "target_languages": {
                            "type": "object",
                            "description": "Optional dict mapping student_id to language code (e.g., {123: 'es', 456: 'en'})"
                        },
                        "channels": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["email", "sms", "both"]},
                            "description": "Communication channels",
                            "default": ["email"]
                        }
                    },
                    "required": ["assignment_id", "student_ids"]
                }
            },
            {
                "name": "translate_assignment_submission",
                "description": "Translate student assignment submission from their language to English (or specified target language).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "submission_text": {"type": "string", "description": "Student's submission text"},
                        "target_language": {
                            "type": "string",
                            "description": "Target language code (default: 'en' for English)",
                            "default": "en"
                        },
                        "source_language": {
                            "type": "string",
                            "description": "Source language code (auto-detected if not provided)"
                        }
                    },
                    "required": ["submission_text"]
                }
            }
        ]
    
    @staticmethod
    def get_all_schemas() -> List[Dict[str, Any]]:
        """Get all widget function schemas including enhancements."""
        schemas = []
        schemas.extend(WidgetFunctionSchemas.get_physical_education_schemas())
        schemas.extend(WidgetFunctionSchemas.get_health_schemas())
        schemas.extend(WidgetFunctionSchemas.get_drivers_ed_schemas())
        schemas.extend(WidgetFunctionSchemas.get_widget_management_schemas())
        schemas.extend(WidgetFunctionSchemas.get_enhancement_schemas())
        return schemas


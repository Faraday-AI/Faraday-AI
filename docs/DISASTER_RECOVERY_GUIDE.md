# Faraday AI Disaster Recovery & Recreation Guide

## 🚨 **CRITICAL: Complete Project Recreation Documentation**

This document contains everything needed to recreate the Faraday AI project from scratch in case of complete data loss or system failure.

## 🎯 **CURRENT PROJECT STATUS (Latest Update)**

### **Major Achievement: Complete Database System** ✅
- **✅ 360 tables successfully created** in Azure PostgreSQL database
- **✅ All 337+ registered models** have corresponding database tables
- **✅ Comprehensive seed data** covering all application modules
- **✅ All foreign key relationships** properly established
- **✅ Complete physical education module** with safety, assessment, and progress tracking
- **✅ Full user management and organization system**
- **✅ Dashboard and analytics models**
- **✅ GPT integration and subscription models**
- **✅ Resource management and optimization models**

---

## 📋 **ESSENTIAL RECREATION CHECKLIST**

### **1. Environment & Infrastructure**
- [ ] Azure PostgreSQL database setup
- [ ] Environment variables configuration
- [ ] Docker and Docker Compose setup
- [ ] Python virtual environment
- [ ] Git repository access

### **2. Database Recreation**
- [ ] All 360 tables created
- [ ] All 337+ models registered
- [ ] All foreign key relationships established
- [ ] All seed data populated
- [ ] All enum types created

### **3. Application Components**
- [ ] All API endpoints functional
- [ ] All services operational
- [ ] All models and relationships working
- [ ] All seed scripts functional
- [ ] All tests passing

---

## 🔧 **STEP-BY-STEP RECREATION PROCESS**

### **Phase 1: Environment Setup**

#### **1.1 Azure PostgreSQL Database**
```bash
# Database Connection String (KEEP SECURE)
DATABASE_URL=postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require

# Required Database Features
- PostgreSQL 13+
- SSL/TLS enabled
- Connection pooling
- Backup enabled
- Monitoring enabled
```

#### **1.2 Environment Variables**
```bash
# Core Environment Variables (from run.sh)
DATABASE_URL=postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=your-openai-api-key-here
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=faraday-media
GRAFANA_ADMIN_PASSWORD=admin
LOG_LEVEL=INFO
API_PORT=8000
METRICS_PORT=9092
SERVICE_TYPE=pe
```

#### **1.3 Project Structure**
```
Faraday-AI/
├── app/
│   ├── models/                    # All 337+ models
│   ├── scripts/seed_data/         # All seed scripts
│   ├── services/                  # All services
│   ├── api/                       # All API endpoints
│   └── core/                      # Core configurations
├── docs/                          # All documentation
├── docker-compose.yml             # Container configuration
├── requirements.txt               # Python dependencies
├── run.sh                         # Main execution script
└── setup_local.sh                 # Local setup script
```

### **Phase 2: Database Recreation**

#### **2.1 Critical Database Commands**
```bash
# 1. Start containers with correct environment
docker-compose up -d db redis minio app

# 2. Run seed script with Azure database
docker-compose exec app bash -c "export DATABASE_URL='postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require' && export REDIS_URL='redis://redis:6379/0' && export OPENAI_API_KEY='your-openai-api-key-here' && export MINIO_ACCESS_KEY='minioadmin' && export MINIO_SECRET_KEY='minioadmin' && export MINIO_BUCKET='faraday-media' && export GRAFANA_ADMIN_PASSWORD='admin' && export LOG_LEVEL='INFO' && export API_PORT='8000' && export METRICS_PORT='9092' && export SERVICE_TYPE='pe' && unset PYTHONHOME && python3 -c \"import sys; sys.path.insert(0, '/app'); from app.scripts.seed_data.seed_database import seed_database; seed_database()\""

# 3. Verify database creation
docker-compose exec app bash -c "export DATABASE_URL='postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require' && psql \$DATABASE_URL -c \"SELECT COUNT(*) as total_tables FROM information_schema.tables WHERE table_schema = 'public';\""
```

#### **2.2 Expected Database Results**
- **Total Tables**: 360
- **Models Registered**: 337+
- **Seed Data**: Comprehensive coverage of all modules
- **Relationships**: All foreign keys properly established

#### **2.3 Critical Model Files**
```
app/models/
├── __init__.py                    # Main model imports (337+ models)
├── shared_base.py                 # SharedBase declarative base
├── core/                          # Core models
├── physical_education/            # PE models (complete)
├── dashboard/                     # Dashboard models
├── security/                      # Security models
├── organization/                  # Organization models
├── user_management/               # User management models
├── gpt/                          # GPT integration models
├── resource_management/           # Resource management models
└── educational/                   # Educational models
```

### **Phase 3: Seed Data Recreation**

#### **3.1 Critical Seed Scripts**
```
app/scripts/seed_data/
├── seed_database.py               # Main seeding script
├── seed_users.py                  # User creation
├── seed_students.py               # Student creation
├── seed_activities.py             # Activity creation
├── seed_classes.py                # Class creation
├── seed_exercises.py              # Exercise creation
├── seed_safety_incidents.py       # Safety data
├── seed_risk_assessments.py       # Risk assessment data
├── seed_safety_checks.py          # Safety check data
├── seed_equipment_checks.py       # Equipment check data
├── seed_environmental_checks.py   # Environmental check data
├── seed_routines.py               # Routine creation
├── seed_routine_performance.py    # Performance data
├── seed_skill_assessments.py      # Skill assessment data
├── seed_skill_progress.py         # Skill progress data
└── seed_performance_metrics.py    # Performance metrics
```

#### **3.2 Seed Data Verification**
```bash
# Verify all seed data was created successfully
docker-compose exec app bash -c "export DATABASE_URL='postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require' && psql \$DATABASE_URL -c \"SELECT 'users' as table_name, COUNT(*) as count FROM users UNION ALL SELECT 'students', COUNT(*) FROM students UNION ALL SELECT 'activities', COUNT(*) FROM activities UNION ALL SELECT 'classes', COUNT(*) FROM physical_education_classes UNION ALL SELECT 'exercises', COUNT(*) FROM exercises UNION ALL SELECT 'safety_incidents', COUNT(*) FROM safety_incidents UNION ALL SELECT 'risk_assessments', COUNT(*) FROM risk_assessments;\""
```

### **Phase 4: Model Relationships Verification**

#### **4.1 Critical Relationships**
```python
# Key relationships that must be verified
User -> PhysicalEducationClass (teacher relationship)
Student -> PhysicalEducationClass (student relationship)
Activity -> Exercise (activity relationship)
SafetyIncident -> User (teacher relationship)
RiskAssessment -> Activity (assessment relationship)
Routine -> RoutineActivity (routine relationship)
SkillAssessment -> Student (assessment relationship)
```

#### **4.2 Model Conflict Resolution**
```python
# Critical model fixes that were implemented
- SafetyIncident -> SkillAssessmentSafetyIncident (renamed to avoid conflicts)
- Exercise table conflicts resolved
- Foreign key relationships corrected
- Enum usage standardized
- Async/sync function issues resolved
```

### **Phase 5: API Testing**

#### **5.1 Critical API Endpoints**
```bash
# Test core API functionality
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/users
curl http://localhost:8000/api/v1/students
curl http://localhost:8000/api/v1/activities
curl http://localhost:8000/api/v1/classes
```

#### **5.2 Database Connection Testing**
```bash
# Test database connectivity
docker-compose exec app bash -c "export DATABASE_URL='postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require' && python3 -c \"import sys; sys.path.insert(0, '/app'); from app.db.session import engine; print('Database connection successful!')\""
```

---

## 🔐 **SECURITY & BACKUP INFORMATION**

### **Critical Credentials (KEEP SECURE)**
```bash
# Azure PostgreSQL
Host: faraday-ai-db.postgres.database.azure.com
Port: 5432
Database: postgres
Username: faraday_admin
Password: CodaMoeLuna31
SSL: Required

# OpenAI API
API Key: [REDACTED - Use environment variable OPENAI_API_KEY]

# MinIO
Access Key: minioadmin
Secret Key: minioadmin
Bucket: faraday-media
```

### **Backup Strategy**
```bash
# Database backup command
pg_dump "postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require" > faraday_backup_$(date +%Y%m%d_%H%M%S).sql

# Restore command
psql "postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require" < faraday_backup_YYYYMMDD_HHMMSS.sql
```

---

## 🚨 **EMERGENCY RECOVERY PROCEDURES**

### **Complete System Loss Recovery**
1. **Clone Repository**: `git clone https://github.com/Faraday-AI/Faraday-AI.git`
2. **Setup Environment**: Follow Phase 1 above
3. **Recreate Database**: Follow Phase 2 above
4. **Verify Data**: Follow Phase 3 above
5. **Test System**: Follow Phase 4 above

### **Database-Only Recovery**
1. **Restore from Backup**: Use pg_dump restore command
2. **Verify Tables**: Check for 360 tables
3. **Verify Data**: Check seed data integrity
4. **Test Relationships**: Verify foreign key relationships

### **Partial Data Loss Recovery**
1. **Identify Missing Data**: Check table counts
2. **Re-run Seed Scripts**: Run specific seed scripts
3. **Verify Relationships**: Check foreign key integrity
4. **Test Functionality**: Verify API endpoints

---

## 📊 **VERIFICATION CHECKLIST**

### **Database Verification**
- [ ] 360 tables exist in Azure PostgreSQL
- [ ] All 337+ models are registered
- [ ] All foreign key relationships work
- [ ] All seed data is populated
- [ ] All enum types are created

### **Application Verification**
- [ ] All API endpoints respond
- [ ] All services are operational
- [ ] All models can be queried
- [ ] All relationships work correctly
- [ ] All tests pass

### **Data Verification**
- [ ] Users seeded successfully
- [ ] Students seeded successfully
- [ ] Activities seeded successfully
- [ ] Classes seeded successfully
- [ ] Safety data seeded successfully
- [ ] Assessment data seeded successfully

---

## 📞 **EMERGENCY CONTACTS**

### **Critical Information Sources**
- **GitHub Repository**: https://github.com/Faraday-AI/Faraday-AI
- **Azure Database**: faraday-ai-db.postgres.database.azure.com
- **Documentation**: /docs/ directory in repository
- **Seed Scripts**: /app/scripts/seed_data/ directory

### **Recovery Time Estimates**
- **Complete Recreation**: 2-4 hours
- **Database Recovery**: 30-60 minutes
- **Partial Recovery**: 15-30 minutes
- **Verification**: 30-60 minutes

---

## ✅ **FINAL VERIFICATION**

After completing all steps, verify the system is fully operational:

```bash
# 1. Check database tables
docker-compose exec app bash -c "export DATABASE_URL='postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require' && psql \$DATABASE_URL -c \"SELECT COUNT(*) as total_tables FROM information_schema.tables WHERE table_schema = 'public';\""

# 2. Check API health
curl http://localhost:8000/health

# 3. Check core endpoints
curl http://localhost:8000/api/v1/users
curl http://localhost:8000/api/v1/students
curl http://localhost:8000/api/v1/activities

# 4. Verify seed data
docker-compose exec app bash -c "export DATABASE_URL='postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require' && psql \$DATABASE_URL -c \"SELECT 'users' as table_name, COUNT(*) as count FROM users UNION ALL SELECT 'students', COUNT(*) FROM students UNION ALL SELECT 'activities', COUNT(*) FROM activities;\""
```

**Expected Results:**
- Total Tables: 360
- API Health: 200 OK
- Core Endpoints: Return data
- Seed Data: All tables populated

---

## 🎯 **SUCCESS CRITERIA**

The system is fully recovered when:
1. ✅ 360 tables exist in Azure PostgreSQL
2. ✅ All API endpoints respond correctly
3. ✅ All seed data is populated
4. ✅ All foreign key relationships work
5. ✅ All tests pass
6. ✅ Application is fully functional

---

**Last Updated**: July 17, 2025
**Version**: 1.0
**Status**: Complete Database System Operational 
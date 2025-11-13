# LMS Data Sync Capabilities

**Date:** November 13, 2025  
**Status:** Planning Phase  
**Purpose:** Document what data can be imported/exported/synced from each LMS system

---

## Overview

Yes! When integrating with PowerSchool, Schoology, and Google Classroom (and all other LMS systems), we will be able to sync comprehensive data **if the teacher/user has an account on that platform from their school already**. The OAuth authentication will use their existing school account, and we'll have access to data based on their permissions.

---

## Authentication & Permissions

### How It Works

1. **Teacher/User logs in** with their existing school LMS account (OAuth)
2. **We receive an access token** with permissions based on their role
3. **We can access data** that their account has permission to view
4. **Data sync happens** based on their account's access level

### Permission Levels

- **Teacher Role:** Can access their own courses, students, grades, rosters
- **Admin Role:** Can access all courses, students, grades, rosters (if API permissions allow)
- **Limited Access:** May only see specific courses or students they're assigned to

---

## Data Sync Capabilities by LMS System

### ✅ PowerSchool Integration

**Available Data:**

1. **Class Rosters** ✅
   - Student enrollments
   - Course sections
   - Student IDs
   - Enrollment dates
   - Section assignments

2. **Student Demographics** ✅
   - Student names (first, last, middle)
   - Student IDs (local and state)
   - Date of birth
   - Gender
   - Grade level
   - School assignment
   - Enrollment status
   - Address information (if permissions allow)

3. **Parent/Guardian Contact Information** ✅
   - Parent/guardian names
   - Email addresses
   - Phone numbers (home, work, mobile)
   - Relationship to student
   - Emergency contacts
   - Contact preferences

4. **Grades** ✅
   - Assignment grades
   - Course grades
   - Final grades
   - Grade history
   - Grade comments
   - Grade passback (send grades from Faraday to PowerSchool)

5. **Additional Data** ✅
   - Attendance records
   - Discipline records (if permissions allow)
   - Special programs/504/IEP information (if permissions allow)
   - Schedule information
   - Teacher assignments

**API Endpoints Available:**
- `/ws/v1/district/student` - Student data
- `/ws/v1/district/guardian` - Parent/guardian data
- `/ws/v1/section` - Section/roster data
- `/ws/v1/gradebook/assignment` - Assignment grades
- `/ws/v1/gradebook/finalgrade` - Final grades

**Permissions Required:**
- `Student Information` read access
- `Guardian Information` read access
- `Gradebook` read/write access (for grade passback)

---

### ✅ Schoology Integration

**Available Data:**

1. **Class Rosters** ✅
   - Student enrollments
   - Course sections
   - Student IDs
   - Enrollment status
   - Section assignments

2. **Student Demographics** ✅
   - Student names
   - Student IDs
   - Email addresses
   - Profile information
   - School assignment
   - Grade level

3. **Parent/Guardian Contact Information** ✅
   - Parent/guardian names
   - Email addresses
   - Phone numbers
   - Relationship to student
   - Contact preferences

4. **Grades** ✅
   - Assignment grades
   - Course grades
   - Grade history
   - Grade comments
   - Grade passback (send grades from Faraday to Schoology)

5. **Additional Data** ✅
   - Attendance (if Schoology Attendance is enabled)
   - Course materials
   - Assignment submissions

**API Endpoints Available:**
- `/users` - User/student data
- `/users/{id}/parents` - Parent/guardian data
- `/sections/{id}/enrollments` - Roster data
- `/sections/{id}/grades` - Grade data
- `/sections/{id}/assignments` - Assignment data

**Permissions Required:**
- `Read user information`
- `Read parent information`
- `Read section enrollments`
- `Read/write grades`

---

### ✅ Google Classroom Integration

**Available Data:**

1. **Class Rosters** ✅
   - Student enrollments
   - Course participants
   - Student IDs
   - Enrollment status
   - Role (student, teacher, guardian)

2. **Student Demographics** ⚠️ Limited
   - Student names
   - Email addresses
   - Profile photos
   - **Note:** Google Classroom has limited demographic data compared to SIS systems

3. **Parent/Guardian Contact Information** ✅
   - Guardian email addresses (if guardians are invited to Classroom)
   - Guardian names
   - **Note:** Guardian access must be enabled by school admin

4. **Grades** ✅
   - Assignment grades
   - Course grades
   - Grade history
   - Grade passback (send grades from Faraday to Google Classroom)

5. **Additional Data** ✅
   - Course materials
   - Assignment submissions
   - Student work
   - Announcements

**API Endpoints Available:**
- `/v1/courses/{id}/students` - Student roster
- `/v1/courses/{id}/teachers` - Teacher roster
- `/v1/courses/{id}/courseWork` - Assignments
- `/v1/courses/{id}/courseWork/{id}/studentSubmissions` - Submissions and grades
- `/v1/userProfiles/{id}` - User profile data

**Permissions Required:**
- `classroom.courses.readonly` - Read courses
- `classroom.rosters.readonly` - Read rosters
- `classroom.profile.emails` - Read email addresses
- `classroom.coursework.me` - Read/write coursework
- `classroom.grades` - Read/write grades

**Limitations:**
- Google Classroom is primarily a course management tool, not a full SIS
- Demographic data is limited compared to PowerSchool (which is a full SIS)
- Parent/guardian data depends on guardian access being enabled

---

### ✅ Canvas Integration

**Available Data:**

1. **Class Rosters** ✅
   - Student enrollments
   - Course sections
   - Student IDs
   - Enrollment status

2. **Student Demographics** ⚠️ Limited
   - Student names
   - Email addresses
   - SIS ID (if synced from SIS)
   - **Note:** Canvas is an LMS, not an SIS, so demographic data is limited

3. **Parent/Guardian Contact Information** ⚠️ Limited
   - Observer accounts (parent/guardian accounts linked to students)
   - Observer email addresses
   - **Note:** Depends on observer accounts being set up

4. **Grades** ✅
   - Assignment grades
   - Course grades
   - Grade history
   - Grade passback

**API Endpoints Available:**
- `/api/v1/courses/{id}/students` - Student roster
- `/api/v1/courses/{id}/enrollments` - Enrollments
- `/api/v1/courses/{id}/assignments` - Assignments
- `/api/v1/courses/{id}/submissions` - Submissions and grades
- `/api/v1/users/{id}/observees` - Observer (parent) relationships

---

### ✅ Moodle Integration

**Available Data:**

1. **Class Rosters** ✅
   - Student enrollments
   - Course participants
   - Student IDs

2. **Student Demographics** ⚠️ Limited
   - Student names
   - Email addresses
   - Profile information
   - **Note:** Moodle is an LMS, demographic data depends on what's entered

3. **Parent/Guardian Contact Information** ⚠️ Limited
   - Depends on Moodle configuration
   - May require custom fields or plugins

4. **Grades** ✅
   - Assignment grades
   - Course grades
   - Grade passback

---

### ✅ Blackboard Integration

**Available Data:**

1. **Class Rosters** ✅
   - Student enrollments
   - Course members
   - Student IDs

2. **Student Demographics** ⚠️ Limited
   - Student names
   - Email addresses
   - **Note:** Blackboard Learn is an LMS, demographic data depends on SIS integration

3. **Parent/Guardian Contact Information** ⚠️ Limited
   - Depends on Blackboard configuration and SIS integration

4. **Grades** ✅
   - Assignment grades
   - Course grades
   - Grade passback

---

## Data Sync Comparison

| Data Type | PowerSchool | Schoology | Google Classroom | Canvas | Moodle | Blackboard |
|-----------|-------------|-----------|------------------|--------|--------|------------|
| **Class Rosters** | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Student Demographics** | ✅ Full | ✅ Good | ⚠️ Limited | ⚠️ Limited | ⚠️ Limited | ⚠️ Limited |
| **Parent Contact Info** | ✅ Full | ✅ Full | ✅ If enabled | ⚠️ If observers set up | ⚠️ Depends | ⚠️ Depends |
| **Grades** | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Attendance** | ✅ Full | ⚠️ If enabled | ❌ No | ⚠️ If enabled | ⚠️ If enabled | ⚠️ If enabled |
| **Discipline** | ✅ If permissions | ❌ No | ❌ No | ❌ No | ❌ No | ⚠️ If enabled |

**Key Differences:**
- **PowerSchool & Schoology:** Full SIS systems with comprehensive student and parent data
- **Google Classroom, Canvas, Moodle, Blackboard:** LMS systems with limited demographic data (unless integrated with an SIS)

---

## Implementation Strategy

### Data Sync Workflow

1. **Initial Sync (Import)**
   ```
   Teacher connects LMS account → OAuth authentication → 
   Fetch courses → Fetch rosters → Fetch student data → 
   Fetch parent data → Store in Faraday database
   ```

2. **Ongoing Sync (Bidirectional)**
   ```
   Periodic sync: Check for new enrollments, updated grades, 
   changed contact info → Update Faraday database
   
   Grade passback: Teacher grades in Faraday → 
   Send to LMS → Update LMS gradebook
   ```

3. **Data Mapping**
   ```
   LMS Student → Faraday Student
   LMS Parent → Faraday Parent/Guardian
   LMS Course → Faraday Class
   LMS Assignment → Faraday Assignment
   LMS Grade → Faraday Grade
   ```

### Data Storage in Faraday

**Database Tables:**
- `students` - Student demographics and information
- `parents` or `guardians` - Parent/guardian contact information
- `classes` - Course/class information
- `enrollments` - Student-class relationships
- `assignments` - Assignment information
- `grades` - Grade information
- `lms_student_mappings` - Map LMS student ID to Faraday student ID
- `lms_parent_mappings` - Map LMS parent ID to Faraday parent ID

---

## Privacy & Security Considerations

### Data Access

- **Only sync data the teacher's account has permission to view**
- **Respect LMS permission levels** (teacher vs. admin)
- **Store encrypted tokens** (already implemented)
- **Log all data access** for audit purposes

### FERPA Compliance

- **Student data:** Only sync if teacher has legitimate educational interest
- **Parent data:** Only sync contact information needed for communication
- **Grade data:** Only sync grades for courses the teacher teaches
- **Demographic data:** Only sync if necessary for educational purposes

### Data Retention

- **Sync data on-demand** (when teacher requests)
- **Periodic sync** (daily/weekly, configurable)
- **Data retention policy** (delete when teacher disconnects LMS)

---

## API Endpoints to Implement

### Roster Sync
- `GET /api/v1/integration/lms/{lms_type}/courses/{course_id}/roster` - Get class roster
- `POST /api/v1/integration/lms/{lms_type}/courses/{course_id}/sync-roster` - Sync roster to Faraday
- `GET /api/v1/integration/lms/{lms_type}/students` - Get all students (if permissions allow)

### Parent/Guardian Sync
- `GET /api/v1/integration/lms/{lms_type}/students/{student_id}/parents` - Get parent info
- `POST /api/v1/integration/lms/{lms_type}/sync-parents` - Sync parent data to Faraday

### Demographics Sync
- `GET /api/v1/integration/lms/{lms_type}/students/{student_id}/demographics` - Get demographics
- `POST /api/v1/integration/lms/{lms_type}/sync-demographics` - Sync demographics to Faraday

### Grade Sync
- `GET /api/v1/integration/lms/{lms_type}/courses/{course_id}/grades` - Get grades
- `POST /api/v1/integration/lms/{lms_type}/grades/passback` - Send grades to LMS
- `POST /api/v1/integration/lms/{lms_type}/sync-grades` - Sync grades bidirectionally

---

## Summary

**Yes, we can import/export/sync:**

✅ **Class Rosters** - All systems  
✅ **Grades** - All systems (bidirectional)  
✅ **Parent Contact Information** - PowerSchool & Schoology (full), others (if configured)  
✅ **Student Demographics** - PowerSchool & Schoology (full), others (limited)  
✅ **Other Data** - Varies by system and permissions

**Requirements:**
- Teacher/user must have an account on the LMS platform from their school
- OAuth authentication uses their existing school account
- Data access is based on their account's permissions
- PowerSchool and Schoology provide the most comprehensive data (they're full SIS systems)

---

**Status:** Ready to implement comprehensive data sync for all LMS systems ✅


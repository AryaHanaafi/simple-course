import json
import os

file_path = "c:/UDINUS/SEMESTER6/Pemrograman Sisi Server/simple-lms/simple_lms_postman.json"

with open(file_path, 'r') as f:
    data = json.load(f)

# Find folders
public_folder = next(item for item in data['item'] if item['name'] == '2. Public Data')
student_folder = next(item for item in data['item'] if item['name'] == '3. Student Space (Requires Login)')
instructor_folder = next(item for item in data['item'] if item['name'] == '4. Instructor Space (Requires Login)')
admin_folder = next(item for item in data['item'] if item['name'] == '5. Admin Command (Requires Login)')

# Public Additions
public_folder['item'].extend([
    {
        "name": "Get Learning Paths",
        "request": {
            "method": "GET",
            "url": {"raw": "http://localhost:8080/api/learning-paths", "protocol": "http", "host": ["localhost"], "port": "8080", "path": ["api", "learning-paths"]}
        }
    },
    {
        "name": "Get Learning Path Detail",
        "request": {
            "method": "GET",
            "url": {"raw": "http://localhost:8080/api/learning-paths/1", "protocol": "http", "host": ["localhost"], "port": "8080", "path": ["api", "learning-paths", "1"]}
        }
    }
])

# Student Additions
student_folder['item'].extend([
    {
        "name": "Mark Lesson Complete",
        "request": {
            "method": "POST",
            "url": {"raw": "http://localhost:8080/api/student/lesson/1/complete", "protocol": "http", "host": ["localhost"], "port": "8080", "path": ["api", "student", "lesson", "1", "complete"]}
        }
    },
    {
        "name": "Update Profile",
        "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": {
                "mode": "raw",
                "raw": "{\n  \"first_name\": \"John\",\n  \"last_name\": \"Doe\",\n  \"email\": \"john@example.com\"\n}"
            },
            "url": {"raw": "http://localhost:8080/api/profile/update", "protocol": "http", "host": ["localhost"], "port": "8080", "path": ["api", "profile", "update"]}
        }
    }
])

# Instructor Additions
instructor_folder['item'].extend([
    {
        "name": "Get Instructor Stats",
        "request": {
            "method": "GET",
            "url": {"raw": "http://localhost:8080/api/instructor/stats", "protocol": "http", "host": ["localhost"], "port": "8080", "path": ["api", "instructor", "stats"]}
        }
    },
    {
        "name": "Create Announcement",
        "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": {
                "mode": "raw",
                "raw": "{\n  \"title\": \"Welcome to the course!\",\n  \"content\": \"Please read the syllabus.\"\n}"
            },
            "url": {"raw": "http://localhost:8080/api/instructor/courses/1/announcements", "protocol": "http", "host": ["localhost"], "port": "8080", "path": ["api", "instructor", "courses", "1", "announcements"]}
        }
    },
    {
        "name": "Create Assignment",
        "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": {
                "mode": "raw",
                "raw": "{\n  \"title\": \"Final Project\",\n  \"instructions\": \"Build an API.\",\n  \"max_score\": 100\n}"
            },
            "url": {"raw": "http://localhost:8080/api/instructor/lessons/1/assignments", "protocol": "http", "host": ["localhost"], "port": "8080", "path": ["api", "instructor", "lessons", "1", "assignments"]}
        }
    },
    {
        "name": "Delete Course",
        "request": {
            "method": "DELETE",
            "url": {"raw": "http://localhost:8080/api/instructor/courses/1/delete", "protocol": "http", "host": ["localhost"], "port": "8080", "path": ["api", "instructor", "courses", "1", "delete"]}
        }
    }
])

# Admin Additions
admin_folder['item'].extend([
    {
        "name": "Create Category",
        "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": {
                "mode": "raw",
                "raw": "{\n  \"name\": \"Data Science\",\n  \"description\": \"Learn Data\"\n}"
            },
            "url": {"raw": "http://localhost:8080/api/admin/categories/create", "protocol": "http", "host": ["localhost"], "port": "8080", "path": ["api", "admin", "categories", "create"]}
        }
    },
    {
        "name": "Delete Category",
        "request": {
            "method": "DELETE",
            "url": {"raw": "http://localhost:8080/api/admin/categories/1/delete", "protocol": "http", "host": ["localhost"], "port": "8080", "path": ["api", "admin", "categories", "1", "delete"]}
        }
    },
    {
        "name": "Create User",
        "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": {
                "mode": "raw",
                "raw": "{\n  \"username\": \"newuser\",\n  \"password\": \"pass123\",\n  \"email\": \"new@user.com\",\n  \"role\": \"student\"\n}"
            },
            "url": {"raw": "http://localhost:8080/api/admin/users/create", "protocol": "http", "host": ["localhost"], "port": "8080", "path": ["api", "admin", "users", "create"]}
        }
    },
    {
        "name": "Delete User",
        "request": {
            "method": "DELETE",
            "url": {"raw": "http://localhost:8080/api/admin/users/1/delete", "protocol": "http", "host": ["localhost"], "port": "8080", "path": ["api", "admin", "users", "1", "delete"]}
        }
    }
])

with open(file_path, 'w') as f:
    json.dump(data, f, indent=2)

print("Postman collection updated successfully!")

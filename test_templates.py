import os
import django
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

# Create dummy users for testing
try:
    student = User.objects.create_user(username='test_student', password='password', role='student')
    instructor = User.objects.create_user(username='test_instructor', password='password', role='instructor')
    admin = User.objects.create_superuser(username='test_admin', password='password', role='superadmin', email='a@a.com')
except Exception:
    student = User.objects.get(username='test_student')
    instructor = User.objects.get(username='test_instructor')
    admin = User.objects.get(username='test_admin')

urls_to_test = [
    # Public / Auth
    ('login', None, None),
    ('register', None, None),
    
    # Student
    ('student_dashboard', None, student),
    ('student_catalog', None, student),
    ('learning_paths_list', None, student),
    ('user_profile', None, student),
    
    # Instructor
    ('instructor_dashboard', None, instructor),
    ('create_course', None, instructor),
    
    # Admin
    ('admin_dashboard', None, admin),
    ('admin_categories', None, admin),
    ('admin_category_create', None, admin),
    ('admin_users', None, admin),
    ('admin_user_create', None, admin),
]

client = Client()
errors = []

print("Running deep template & view tests...")

for url_name, kwargs, user in urls_to_test:
    if user:
        client.login(username=user.username, password='password')
    else:
        client.logout()
        
    try:
        url = reverse(url_name, kwargs=kwargs)
        response = client.get(url)
        if response.status_code not in [200, 302]:
            errors.append(f"[ERROR] {url_name} returned status {response.status_code}")
        else:
            print(f"[OK] {url_name} rendered successfully")
    except Exception as e:
        errors.append(f"[EXCEPTION] {url_name}: {e}")

if errors:
    print("\n--- ERRORS FOUND ---")
    for err in errors:
        print(err)
    sys.exit(1)
else:
    print("\nAll basic views rendered without 500 errors!")

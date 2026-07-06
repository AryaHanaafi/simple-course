import os
import django
import random
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from courses.models import User, Course, Section, Lesson, Category, SiteSetting

def run_seed():
    print("Clearing old data...")
    Course.objects.all().delete()
    Category.objects.all().delete()
    User.objects.exclude(username='admin').delete()
    
    print("Seeding SiteSettings...")
    SiteSetting.objects.all().delete()
    SiteSetting.objects.create(
        site_name="NextGen Pro",
        announcement_banner="Welcome to NextGen Pro Learning! Enjoy free premium courses.",
        is_banner_active=True
    )
    
    print("Seeding Categories...")
    cat_dev = Category.objects.create(name="Development", description="Coding and Software Engineering")
    cat_design = Category.objects.create(name="Design", description="UI/UX and Graphic Design")
    cat_biz = Category.objects.create(name="Business", description="Management and Entrepreneurship")
    categories = [cat_dev, cat_design, cat_biz]
    
    print("Seeding Users (Max 10 total users including admin)...")
    # 1 admin already exists, so we create 2 instructors + 7 students = 10 users total.
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@lms.com', 'admin123', role='superadmin')
    
    inst1 = User.objects.create_user(username='inst1', password='password123', email='inst1@lms.com', role='instructor', first_name="Budi", last_name="Santoso")
    inst2 = User.objects.create_user(username='inst2', password='password123', email='inst2@lms.com', role='instructor', first_name="Siti", last_name="Aminah")
    instructors = [inst1, inst2]
    
    for i in range(1, 8):
        User.objects.create_user(
            username=f'student{i}', 
            password='password123', 
            email=f'student{i}@lms.com', 
            role='student',
            first_name=f"Siswa",
            last_name=f"{i}"
        )
    
    print("Seeding Courses (Max 10)...")
    course_data = [
        {"title": "Mastering Python", "cat": cat_dev, "diff": "intermediate"},
        {"title": "Web Dev for Beginners", "cat": cat_dev, "diff": "beginner"},
        {"title": "Advanced Django", "cat": cat_dev, "diff": "advanced"},
        {"title": "UI/UX Fundamentals", "cat": cat_design, "diff": "beginner"},
        {"title": "Figma Pro", "cat": cat_design, "diff": "intermediate"},
        {"title": "Digital Marketing", "cat": cat_biz, "diff": "beginner"},
        {"title": "Startup Leadership", "cat": cat_biz, "diff": "advanced"},
        {"title": "Data Science Intro", "cat": cat_dev, "diff": "beginner"},
        {"title": "Graphic Design Masterclass", "cat": cat_design, "diff": "advanced"},
        {"title": "Business Analytics", "cat": cat_biz, "diff": "intermediate"},
    ]
    
    for i, data in enumerate(course_data):
        course = Course.objects.create(
            title=data["title"],
            description=f"Learn everything about {data['title']} in this comprehensive course.",
            difficulty=data["diff"],
            category=data["cat"],
            status="published",
            instructor=random.choice(instructors)
        )
        
        # Add a section and lesson to each course so it's fully populated
        section1 = Section.objects.create(course=course, title="Module 1: Introduction", order=1)
        Lesson.objects.create(
            section=section1, 
            title="Welcome to the Course", 
            content_format="text", 
            content="This is the introductory lesson. We will cover the basics.", 
            order=1
        )
        
        section2 = Section.objects.create(course=course, title="Module 2: Core Concepts", order=2)
        Lesson.objects.create(
            section=section2, 
            title="Deep Dive", 
            content_format="video", 
            content="<iframe width='560' height='315' src='https://www.youtube.com/embed/dQw4w9WgXcQ' frameborder='0' allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture' allowfullscreen></iframe>", 
            order=1
        )

    print("Seeding Complete! Exactly 10 Users and 10 Courses generated with full data.")

if __name__ == "__main__":
    run_seed()

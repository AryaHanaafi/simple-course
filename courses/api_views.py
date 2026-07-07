import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import User, Course, Category, Enrollment, Progress

@csrf_exempt
def api_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            role = data.get('role', 'student')
            
            if not username or not password:
                return JsonResponse({'status': 'error', 'message': 'Username and password are required'}, status=400)
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'Username already exists'}, status=400)
                
            user = User.objects.create_user(username=username, password=password, email=email, role=role)
            return JsonResponse({'status': 'success', 'message': 'User registered successfully', 'user_id': user.id}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if not request.session.session_key:
                    request.session.save()
                token = request.session.session_key
                return JsonResponse({'status': 'success', 'message': 'Login successful', 'token': token, 'role': user.role, 'username': user.username})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_get_categories(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        data = []
        for cat in categories:
            data.append({
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
                'description': cat.description,
                'total_courses': cat.courses.filter(status='published').count()
            })
        return JsonResponse({'status': 'success', 'data': data})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def api_get_courses(request):
    if request.method == 'GET':
        courses = Course.objects.filter(status='published').select_related('instructor', 'category')
        
        # Filtering
        category_slug = request.GET.get('category')
        search_query = request.GET.get('search')
        
        if category_slug:
            courses = courses.filter(category__slug=category_slug)
        if search_query:
            courses = courses.filter(title__icontains=search_query)
            
        # Pagination
        page = request.GET.get('page', 1)
        limit = request.GET.get('limit', 10)
        paginator = Paginator(courses, limit)
        
        try:
            courses_page = paginator.page(page)
        except PageNotAnInteger:
            courses_page = paginator.page(1)
        except EmptyPage:
            courses_page = paginator.page(paginator.num_pages)
            
        course_list = []
        for c in courses_page:
            course_list.append({
                'id': c.id,
                'title': c.title,
                'description': c.description,
                'difficulty': c.get_difficulty_display(),
                'category': c.category.name if c.category else 'Uncategorized',
                'instructor': c.instructor.username,
                'created_at': c.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
            
        return JsonResponse({
            'status': 'success', 
            'data': course_list,
            'pagination': {
                'total_items': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': courses_page.number,
                'has_next': courses_page.has_next(),
                'has_previous': courses_page.has_previous()
            }
        })
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_get_course_detail(request, course_id):
    if request.method == 'GET':
        course = get_object_or_404(Course, id=course_id, status='published')
        sections = course.sections.all().order_by('order')
        
        curriculum = []
        for sec in sections:
            lessons_data = []
            for les in sec.lessons.all().order_by('order'):
                lessons_data.append({
                    'id': les.id,
                    'title': les.title,
                    'type': les.get_content_format_display()
                })
            curriculum.append({
                'id': sec.id,
                'title': sec.title,
                'lessons': lessons_data
            })
            
        data = {
            'id': course.id,
            'title': course.title,
            'instructor': course.instructor.username,
            'category': course.category.name if course.category else 'Uncategorized',
            'description': course.description,
            'curriculum': curriculum
        }
        return JsonResponse({'status': 'success', 'data': data})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_enroll_course(request, course_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Authentication required. Please login first.'}, status=401)
            
        if request.user.role != 'student':
            return JsonResponse({'status': 'error', 'message': 'Only students can enroll in courses.'}, status=403)
            
        course = get_object_or_404(Course, id=course_id, status='published')
        enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
        
        if created:
            return JsonResponse({'status': 'success', 'message': f'Successfully enrolled in {course.title}'}, status=201)
        else:
            return JsonResponse({'status': 'info', 'message': f'You are already enrolled in {course.title}'}, status=200)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_student_dashboard(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Authentication required. Please login first.'}, status=401)
            
        if request.user.role != 'student':
            return JsonResponse({'status': 'error', 'message': 'Only students have a student dashboard.'}, status=403)
            
        enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
        data = []
        for en in enrollments:
            total_lessons = 0
            completed_lessons = 0
            for sec in en.course.sections.all():
                total_lessons += sec.lessons.count()
                for les in sec.lessons.all():
                    if Progress.objects.filter(enrollment=en, lesson=les, is_completed=True).exists():
                        completed_lessons += 1
                        
            progress_percent = int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0
            
            data.append({
                'course_id': en.course.id,
                'course_title': en.course.title,
                'enrolled_at': en.enrolled_at.strftime("%Y-%m-%d"),
                'progress_percentage': progress_percent
            })
            
        return JsonResponse({'status': 'success', 'data': data, 'student': request.user.username})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_mark_lesson_complete(request, lesson_id):
    from .models import Lesson
    if request.method == 'POST':
        if not request.user.is_authenticated or request.user.role != 'student':
            return JsonResponse({'status': 'error', 'message': 'Student authentication required.'}, status=403)
            
        lesson = get_object_or_404(Lesson, id=lesson_id)
        course = lesson.section.course
        enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
        
        progress, created = Progress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
        progress.is_completed = True
        progress.save()
        
        return JsonResponse({'status': 'success', 'message': 'Lesson marked as complete'})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_get_learning_paths(request):
    from .models import LearningPath
    if request.method == 'GET':
        paths = LearningPath.objects.all()
        data = []
        for path in paths:
            data.append({
                'id': path.id,
                'title': path.title,
                'description': path.description,
                'courses_count': path.path_courses.count()
            })
        return JsonResponse({'status': 'success', 'data': data})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_get_path_detail(request, path_id):
    from .models import LearningPath, LearningPathCourse
    if request.method == 'GET':
        path = get_object_or_404(LearningPath, id=path_id)
        path_courses = LearningPathCourse.objects.filter(learning_path=path).order_by('order')
        
        courses_data = []
        for pc in path_courses:
            courses_data.append({
                'order': pc.order,
                'course_id': pc.course.id,
                'course_title': pc.course.title,
                'difficulty': pc.course.get_difficulty_display(),
                'instructor': pc.course.instructor.username
            })
            
        data = {
            'id': path.id,
            'title': path.title,
            'description': path.description,
            'courses': courses_data
        }
        return JsonResponse({'status': 'success', 'data': data})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_update_profile(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
            
        try:
            data = json.loads(request.body)
            first_name = data.get('first_name', request.user.first_name)
            last_name = data.get('last_name', request.user.last_name)
            email = data.get('email', request.user.email)
            
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.email = email
            request.user.save()
            
            return JsonResponse({'status': 'success', 'message': 'Profile updated successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

# ----------------- INSTRUCTOR API ----------------- #

def api_instructor_courses(request):
    if request.method == 'GET':
        if not request.user.is_authenticated or request.user.role != 'instructor':
            return JsonResponse({'status': 'error', 'message': 'Instructor authentication required.'}, status=403)
            
        courses = Course.objects.filter(instructor=request.user).order_by('-created_at')
        data = [{'id': c.id, 'title': c.title, 'status': c.status} for c in courses]
        return JsonResponse({'status': 'success', 'data': data})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_instructor_create_course(request):
    if request.method == 'POST':
        if not request.user.is_authenticated or request.user.role != 'instructor':
            return JsonResponse({'status': 'error', 'message': 'Instructor authentication required.'}, status=403)
            
        try:
            data = json.loads(request.body)
            title = data.get('title')
            category_id = data.get('category_id')
            difficulty = data.get('difficulty', 'beginner')
            description = data.get('description', '')
            
            if not title or not category_id:
                return JsonResponse({'status': 'error', 'message': 'Title and category_id are required'}, status=400)
                
            category = get_object_or_404(Category, id=category_id)
            course = Course.objects.create(
                title=title, category=category, difficulty=difficulty, 
                description=description, instructor=request.user, status='draft'
            )
            return JsonResponse({'status': 'success', 'message': 'Course created as draft', 'course_id': course.id}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_instructor_create_section(request, course_id):
    from .models import Section
    if request.method == 'POST':
        if not request.user.is_authenticated or request.user.role != 'instructor':
            return JsonResponse({'status': 'error', 'message': 'Instructor authentication required.'}, status=403)
            
        course = get_object_or_404(Course, id=course_id, instructor=request.user)
        try:
            data = json.loads(request.body)
            title = data.get('title')
            if not title:
                return JsonResponse({'status': 'error', 'message': 'Title is required'}, status=400)
                
            section = Section.objects.create(course=course, title=title)
            return JsonResponse({'status': 'success', 'message': 'Section created', 'section_id': section.id}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_instructor_create_lesson(request, section_id):
    from .models import Section, Lesson
    if request.method == 'POST':
        if not request.user.is_authenticated or request.user.role != 'instructor':
            return JsonResponse({'status': 'error', 'message': 'Instructor authentication required.'}, status=403)
            
        section = get_object_or_404(Section, id=section_id, course__instructor=request.user)
        try:
            data = json.loads(request.body)
            title = data.get('title')
            content_format = data.get('content_format', 'text')
            content = data.get('content', '')
            
            if not title:
                return JsonResponse({'status': 'error', 'message': 'Title is required'}, status=400)
                
            lesson = Lesson.objects.create(section=section, title=title, content_format=content_format, content=content)
            return JsonResponse({'status': 'success', 'message': 'Lesson created', 'lesson_id': lesson.id}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_instructor_stats(request):
    if request.method == 'GET':
        if not request.user.is_authenticated or request.user.role != 'instructor':
            return JsonResponse({'status': 'error', 'message': 'Instructor authentication required.'}, status=403)
            
        courses = Course.objects.filter(instructor=request.user)
        total_courses = courses.count()
        active_courses = courses.filter(status='published').count()
        total_enrollments = Enrollment.objects.filter(course__instructor=request.user).count()
        total_students = Enrollment.objects.filter(course__instructor=request.user).values('student').distinct().count()
        
        data = {
            'total_courses': total_courses,
            'active_courses': active_courses,
            'total_enrollments': total_enrollments,
            'total_students': total_students
        }
        return JsonResponse({'status': 'success', 'data': data})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_instructor_create_announcement(request, course_id):
    from .models import CourseAnnouncement
    if request.method == 'POST':
        if not request.user.is_authenticated or request.user.role != 'instructor':
            return JsonResponse({'status': 'error', 'message': 'Instructor authentication required.'}, status=403)
            
        course = get_object_or_404(Course, id=course_id, instructor=request.user)
        try:
            data = json.loads(request.body)
            title = data.get('title')
            content = data.get('content')
            
            if not title or not content:
                return JsonResponse({'status': 'error', 'message': 'Title and content are required'}, status=400)
                
            announcement = CourseAnnouncement.objects.create(course=course, title=title, content=content)
            return JsonResponse({'status': 'success', 'message': 'Announcement created', 'announcement_id': announcement.id}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_instructor_create_assignment(request, lesson_id):
    from .models import Lesson, Assignment
    if request.method == 'POST':
        if not request.user.is_authenticated or request.user.role != 'instructor':
            return JsonResponse({'status': 'error', 'message': 'Instructor authentication required.'}, status=403)
            
        lesson = get_object_or_404(Lesson, id=lesson_id, section__course__instructor=request.user)
        if hasattr(lesson, 'assignment'):
            return JsonResponse({'status': 'error', 'message': 'This lesson already has an assignment.'}, status=400)
            
        try:
            data = json.loads(request.body)
            title = data.get('title')
            instructions = data.get('instructions')
            max_score = data.get('max_score', 100)
            
            if not title or not instructions:
                return JsonResponse({'status': 'error', 'message': 'Title and instructions are required'}, status=400)
                
            assignment = Assignment.objects.create(lesson=lesson, title=title, instructions=instructions, max_score=max_score)
            return JsonResponse({'status': 'success', 'message': 'Assignment created', 'assignment_id': assignment.id}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_instructor_delete_course(request, course_id):
    if request.method == 'DELETE' or (request.method == 'POST' and request.GET.get('_method') == 'DELETE'):
        if not request.user.is_authenticated or request.user.role != 'instructor':
            return JsonResponse({'status': 'error', 'message': 'Instructor authentication required.'}, status=403)
            
        course = get_object_or_404(Course, id=course_id, instructor=request.user)
        course.delete()
        return JsonResponse({'status': 'success', 'message': 'Course deleted successfully'})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
# ----------------- ADMIN API ----------------- #

def api_admin_stats(request):
    if request.method == 'GET':
        if not request.user.is_authenticated or request.user.role != 'superadmin':
            return JsonResponse({'status': 'error', 'message': 'Admin authentication required.'}, status=403)
            
        stats = {
            'total_students': User.objects.filter(role='student').count(),
            'total_instructors': User.objects.filter(role='instructor').count(),
            'total_courses': Course.objects.count(),
            'pending_courses': Course.objects.filter(status='pending_review').count()
        }
        return JsonResponse({'status': 'success', 'data': stats})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_admin_users(request):
    if request.method == 'GET':
        if not request.user.is_authenticated or request.user.role != 'superadmin':
            return JsonResponse({'status': 'error', 'message': 'Admin authentication required.'}, status=403)
            
        users = User.objects.all().order_by('-date_joined')
        data = [{'id': u.id, 'username': u.username, 'full_name': f"{u.first_name} {u.last_name}".strip(), 'email': u.email, 'role': u.role} for u in users]
        return JsonResponse({'status': 'success', 'data': data})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_admin_review_course(request, course_id):
    if request.method == 'PUT':
        if not request.user.is_authenticated or request.user.role != 'superadmin':
            return JsonResponse({'status': 'error', 'message': 'Admin authentication required.'}, status=403)
            
        course = get_object_or_404(Course, id=course_id)
        try:
            data = json.loads(request.body)
            action = data.get('action') # 'approve' or 'reject'
            if action == 'approve':
                course.status = 'published'
            elif action == 'reject':
                course.status = 'draft'
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid action. Use approve or reject.'}, status=400)
                
            course.save()
            return JsonResponse({'status': 'success', 'message': f'Course {course.id} status updated to {course.status}'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_admin_category_create(request):
    if request.method == 'POST':
        if not request.user.is_authenticated or request.user.role != 'superadmin':
            return JsonResponse({'status': 'error', 'message': 'Admin authentication required.'}, status=403)
            
        try:
            data = json.loads(request.body)
            name = data.get('name')
            description = data.get('description', '')
            
            if not name:
                return JsonResponse({'status': 'error', 'message': 'Name is required'}, status=400)
                
            from django.utils.text import slugify
            category = Category.objects.create(name=name, slug=slugify(name), description=description)
            return JsonResponse({'status': 'success', 'message': 'Category created', 'category_id': category.id}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_admin_category_delete(request, category_id):
    if request.method == 'DELETE' or (request.method == 'POST' and request.GET.get('_method') == 'DELETE'):
        if not request.user.is_authenticated or request.user.role != 'superadmin':
            return JsonResponse({'status': 'error', 'message': 'Admin authentication required.'}, status=403)
            
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return JsonResponse({'status': 'success', 'message': 'Category deleted successfully'})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_admin_user_create(request):
    if request.method == 'POST':
        if not request.user.is_authenticated or request.user.role != 'superadmin':
            return JsonResponse({'status': 'error', 'message': 'Admin authentication required.'}, status=403)
            
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email', '')
            password = data.get('password')
            role = data.get('role', 'student')
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')
            
            if not username or not password:
                return JsonResponse({'status': 'error', 'message': 'Username and password are required'}, status=400)
                
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'Username already exists'}, status=400)
                
            user = User.objects.create_user(
                username=username, password=password, email=email, 
                role=role, first_name=first_name, last_name=last_name
            )
            return JsonResponse({'status': 'success', 'message': 'User created', 'user_id': user.id}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def api_admin_user_delete(request, user_id):
    if request.method == 'DELETE' or (request.method == 'POST' and request.GET.get('_method') == 'DELETE'):
        if not request.user.is_authenticated or request.user.role != 'superadmin':
            return JsonResponse({'status': 'error', 'message': 'Admin authentication required.'}, status=403)
            
        user = get_object_or_404(User, id=user_id)
        if user.is_superuser:
            return JsonResponse({'status': 'error', 'message': 'Cannot delete superuser'}, status=400)
            
        user.delete()
        return JsonResponse({'status': 'success', 'message': 'User deleted successfully'})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

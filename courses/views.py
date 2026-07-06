import csv
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import User, Course, Section, Lesson, Prerequisite, QuestionBank, MultipleChoice, Assignment, Enrollment, Progress, AssignmentSubmission, QuizAttempt, Category, SiteSetting, LearningPath
from .forms import CustomLoginForm, CourseForm, SectionForm, LessonForm, CSVUploadForm, UserProfileForm, UserPasswordChangeForm, StudentRegistrationForm, CourseAnnouncementForm, LessonCommentForm, QuestionBankForm, MultipleChoiceForm, AssignmentForm
from .decorators import role_required, superadmin_only, instructor_only, student_only, instructor_or_superadmin
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db.models import Sum, Count, Avg

# ----------------- AUTHENTICATION ----------------- #

def register_view(request):
    if request.user.is_authenticated:
        return redirect_based_on_role(request.user)
        
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome.')
            return redirect('student_catalog')
    else:
        form = StudentRegistrationForm()
    return render(request, 'courses/auth/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect_based_on_role(request.user)
        
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect_based_on_role(user)
    else:
        form = CustomLoginForm()
    return render(request, 'courses/auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def redirect_based_on_role(user):
    if user.role == 'superadmin' or user.is_superuser:
        return redirect('admin_dashboard')
    elif user.role == 'instructor':
        return redirect('instructor_dashboard')
    elif user.role == 'student':
        return redirect('student_dashboard')
    return redirect('student_catalog') # Default fallback

@superadmin_only
def impersonate_user(request, user_id):
    user_to_impersonate = get_object_or_404(User, id=user_id)
    login(request, user_to_impersonate)
    return redirect_based_on_role(user_to_impersonate)


# ----------------- USER PROFILE ----------------- #

@login_required
def user_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'courses/student/profile.html', {'form': form})

@login_required
def user_password_change(request):
    if request.method == 'POST':
        form = UserPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Keep user logged in
            messages.success(request, 'Your password was successfully updated.')
            return redirect('user_profile')
    else:
        form = UserPasswordChangeForm(user=request.user)
    return render(request, 'courses/student/password_change.html', {'form': form})

# ----------------- STUDENT SPACE ----------------- #

def student_catalog(request):
    query = request.GET.get('q', '')
    difficulty = request.GET.get('difficulty', '')
    category_slug = request.GET.get('category', '')
    
    courses_list = Course.objects.filter(status='published')
    
    if query:
        courses_list = courses_list.filter(title__icontains=query)
    if difficulty:
        courses_list = courses_list.filter(difficulty=difficulty)
    if category_slug:
        courses_list = courses_list.filter(category__slug=category_slug)
        
    paginator = Paginator(courses_list.order_by('-created_at'), 6)
    page_number = request.GET.get('page')
    courses = paginator.get_page(page_number)
    
    categories = Category.objects.all().order_by('name')
    
    return render(request, 'courses/student/catalog.html', {
        'courses': courses,
        'query': query,
        'difficulty': difficulty,
        'category': category_slug,
        'categories': categories
    })

@student_only
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, status='published')
    
    # Check prerequisites
    prereqs = Prerequisite.objects.filter(course=course)
    for p in prereqs:
        if p.required_course:
            has_passed = Enrollment.objects.filter(student=request.user, course=p.required_course, is_completed=True).exists()
            if not has_passed:
                return HttpResponse("Prerequisite not met: You must complete " + p.required_course.title)

    Enrollment.objects.get_or_create(student=request.user, course=course)
    return redirect('student_course_detail', course_id=course.id)

@student_only
def student_course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    sections = course.sections.all()
    
    return render(request, 'courses/student/course_detail.html', {
        'course': course,
        'sections': sections,
        'enrollment': enrollment
    })

@student_only
def take_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.section.course
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    
    # Content Dripping Check
    prereqs = Prerequisite.objects.filter(lesson=lesson)
    for p in prereqs:
        if p.required_lesson:
            passed = Progress.objects.filter(enrollment=enrollment, lesson=p.required_lesson, is_completed=True).exists()
            if not passed:
                return HttpResponse("You must complete a previous lesson first.")

    progress, created = Progress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    
    if request.method == 'POST':
        progress.is_completed = True
        progress.save()
        return redirect('student_course_detail', course_id=course.id)

    sections = course.sections.prefetch_related('lessons').all()
    completed_lessons = Progress.objects.filter(enrollment=enrollment, is_completed=True).values_list('lesson_id', flat=True)
    
    return render(request, 'courses/student/lesson_detail.html', {
        'lesson': lesson, 
        'progress': progress,
        'course': course,
        'sections': sections,
        'completed_lessons': list(completed_lessons)
    })


@student_only
def submit_quiz_ajax(request, bank_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            answers = data.get('answers', {})
            
            bank = get_object_or_404(QuestionBank, id=bank_id)
            questions = bank.questions.all()
            
            correct_count = 0
            for q in questions:
                if answers.get(str(q.id)) == q.correct_option:
                    correct_count += 1
                    
            score = (correct_count / questions.count()) * 100 if questions.count() > 0 else 0
            QuizAttempt.objects.create(question_bank=bank, student=request.user, score=score)
            
            return JsonResponse({'status': 'success', 'score': score, 'correct_count': correct_count})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


# ----------------- INSTRUCTOR PANEL ----------------- #

@instructor_only
def instructor_dashboard(request):
    courses_list = Course.objects.filter(instructor=request.user).order_by('-created_at')
    
    # Analytics
    total_courses = courses_list.count()
    total_students = Enrollment.objects.filter(course__instructor=request.user).values('student').distinct().count()
    total_enrollments = Enrollment.objects.filter(course__instructor=request.user).count()
    active_courses = courses_list.filter(status='published').count()
    
    paginator = Paginator(courses_list, 10)
    page_number = request.GET.get('page')
    courses = paginator.get_page(page_number)
    
    context = {
        'courses': courses,
        'total_courses': total_courses,
        'total_students': total_students,
        'total_enrollments': total_enrollments,
        'active_courses': active_courses,
    }
    return render(request, 'courses/instructor/dashboard.html', context)

@instructor_only
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.status = 'draft'
            course.save()
            return redirect('instructor_dashboard')
    else:
        form = CourseForm()
    return render(request, 'courses/instructor/course_form.html', {'form': form})

@instructor_only
def request_course_review(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    course.status = 'pending_review'
    course.save()
    return redirect('instructor_dashboard')

@instructor_only
def csv_upload_students(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            for row in reader:
                if len(row) >= 5:
                    email, fname, lname, uname, pwd = row
                    user, created = User.objects.get_or_create(username=uname, defaults={
                        'email': email, 'first_name': fname, 'last_name': lname, 'role': 'student'
                    })
                    if created:
                        user.set_password(pwd)
                        user.save()
                    Enrollment.objects.get_or_create(student=user, course=course)
            return redirect('instructor_dashboard')
    else:
        form = CSVUploadForm()
    return render(request, 'courses/instructor/csv_upload.html', {'form': form})

@instructor_only
def export_course_grades(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    enrollments = course.enrollments.all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="grades_{course.slug}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'First Name', 'Last Name', 'Progress %', 'Completed'])
    
    for en in enrollments:
        writer.writerow([
            en.student.username, 
            en.student.first_name, 
            en.student.last_name, 
            en.progress_percentage, 
            en.is_completed
        ])
    return response


# ----------------- ADMIN COMMAND CENTER ----------------- #

@superadmin_only
def admin_dashboard(request):
    pending_list = Course.objects.filter(status='pending_review').order_by('-created_at')
    all_list = Course.objects.all().order_by('-created_at')
    
    paginator_pending = Paginator(pending_list, 10)
    page_pending = request.GET.get('page_pending')
    pending_courses = paginator_pending.get_page(page_pending)
    
    paginator_all = Paginator(all_list, 10)
    page_all = request.GET.get('page_all')
    all_courses = paginator_all.get_page(page_all)
    
    stats = {
        'total_students': User.objects.filter(role='student').count(),
        'total_instructors': User.objects.filter(role='instructor').count(),
        'total_courses': all_list.count()
    }
    
    return render(request, 'courses/admin/dashboard.html', {
        'pending_courses': pending_courses,
        'all_courses': all_courses,
        'stats': stats
    })

@superadmin_only
def review_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            course.status = 'published'
        elif action == 'reject':
            course.status = 'draft'
        course.save()
        return redirect('admin_dashboard')
    return render(request, 'courses/admin/course_review.html', {'course': course})
# ----------------- ADMIN USER MANAGEMENT ----------------- #

@superadmin_only
def admin_users(request):
    user_list = User.objects.all().order_by('-date_joined')
    paginator = Paginator(user_list, 10)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    return render(request, 'courses/admin/user_list.html', {'users': users})

@superadmin_only
def admin_user_create(request):
    from django.contrib.auth.forms import UserCreationForm
    from django.contrib.auth.models import Group
    
    if request.method == 'POST':
        # Simple custom logic to create user
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password = request.POST.get('password')
        if username and password and role:
            user = User.objects.create_user(username=username, email=email, password=password, role=role)
            return redirect('admin_users')
    return render(request, 'courses/admin/user_form.html')

@superadmin_only
def admin_user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not user.is_superuser:
        user.delete()
    return redirect('admin_users')


# ----------------- STUDENT DASHBOARD ----------------- #

@student_only
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'courses/student/my_courses.html', {'enrollments': enrollments})

# ----------------- INSTRUCTOR COURSE BUILDER ----------------- #

@instructor_only
def instructor_course_manage(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    sections = course.sections.all().prefetch_related('lessons')
    return render(request, 'courses/instructor/course_manage.html', {'course': course, 'sections': sections})

@instructor_only
def instructor_section_create(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        order = request.POST.get('order', 1)
        Section.objects.create(course=course, title=title, order=order)
        return redirect('instructor_course_manage', course_id=course.id)
    return render(request, 'courses/instructor/section_form.html', {'course': course})

@instructor_only
def instructor_lesson_create(request, section_id):
    section = get_object_or_404(Section, id=section_id, course__instructor=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        content_format = request.POST.get('content_format')
        content = request.POST.get('content')
        order = request.POST.get('order', 1)
        Lesson.objects.create(section=section, title=title, content_format=content_format, content=content, order=order)
        return redirect('instructor_course_manage', course_id=section.course.id)
    return render(request, 'courses/instructor/lesson_form.html', {'section': section})

@instructor_only
def instructor_announcement_create(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        form = CourseAnnouncementForm(request.POST)
        if form.is_valid():
            ann = form.save(commit=False)
            ann.course = course
            ann.save()
            messages.success(request, 'Announcement posted successfully.')
            return redirect('instructor_course_manage', course_id=course.id)
    else:
        form = CourseAnnouncementForm()
    return render(request, 'courses/instructor/form_generic.html', {'form': form, 'title': 'Create Announcement', 'course': course})

@instructor_only
def instructor_quiz_create(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        # Simplify: Just create a bank with the title for now
        title = request.POST.get('title')
        if title:
            QuestionBank.objects.create(course=course, title=title)
            messages.success(request, 'Quiz bank created.')
            return redirect('instructor_course_manage', course_id=course.id)
    return render(request, 'courses/instructor/form_generic.html', {'title': 'Create Quiz Bank', 'course': course, 'is_simple_post': True})

@instructor_only
def instructor_assignment_create(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, section__course__instructor=request.user)
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.lesson = lesson
            assignment.save()
            messages.success(request, 'Assignment attached to lesson.')
            return redirect('instructor_course_manage', course_id=lesson.section.course.id)
    else:
        form = AssignmentForm()
    return render(request, 'courses/instructor/form_generic.html', {'form': form, 'title': f'Add Assignment to {lesson.title}', 'course': lesson.section.course})

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@instructor_only
def api_reorder_lessons(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # data structure: [{'id': 1, 'order': 1}, {'id': 2, 'order': 2}]
            for item in data:
                lesson = Lesson.objects.get(id=item['id'], section__course__instructor=request.user)
                lesson.order = item['order']
                lesson.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)

@instructor_only
def instructor_course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    course.delete()
    return redirect('instructor_dashboard')

@superadmin_only
def admin_course_edit(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/admin/course_edit.html', {'form': form, 'course': course})

@superadmin_only
def admin_course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    return redirect('admin_dashboard')
# ----------------- ADMIN CATEGORIES ----------------- #

@superadmin_only
def admin_categories(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'courses/admin/category_list.html', {'categories': categories})

@superadmin_only
def admin_category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:
            Category.objects.create(name=name, description=description)
            return redirect('admin_categories')
    return render(request, 'courses/admin/category_form.html')

@superadmin_only
def admin_category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        category.save()
        return redirect('admin_categories')
    return render(request, 'courses/admin/category_form.html', {'category': category})

@superadmin_only
def admin_category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('admin_categories')

# ----------------- ADMIN USER EXTENSIONS ----------------- #

@superadmin_only
def admin_user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.role = request.POST.get('role')
        user.save()
        return redirect('admin_users')
    return render(request, 'courses/admin/user_edit.html', {'user_obj': user})

@superadmin_only
def admin_user_reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        password = request.POST.get('password')
        if password:
            user.set_password(password)
            user.save()
            return redirect('admin_users')
    return render(request, 'courses/admin/user_reset_password.html', {'user_obj': user})

# ----------------- SITE SETTINGS ----------------- #

@superadmin_only
def admin_site_settings(request):
    setting = SiteSetting.objects.first()
    if not setting:
        setting = SiteSetting.objects.create(site_name="NextGen Pro Learning")
        
    if request.method == 'POST':
        setting.site_name = request.POST.get('site_name')
        setting.announcement_banner = request.POST.get('announcement_banner')
        setting.is_banner_active = request.POST.get('is_banner_active') == 'on'
        setting.save()
        return redirect('admin_dashboard')
        
# ----------------- LEARNING PATHS ----------------- #

def learning_paths_list(request):
    paths = LearningPath.objects.all().order_by('-created_at')
    return render(request, 'courses/student/learning_paths.html', {'paths': paths})

def learning_path_detail(request, slug):
    path = get_object_or_404(LearningPath, slug=slug)
    path_courses = path.path_courses.select_related('course').order_by('order')
    
    # Optional: check if user is enrolled in these courses
    enrolled_course_ids = []
    if request.user.is_authenticated:
        enrolled_course_ids = Enrollment.objects.filter(student=request.user, course__in=[pc.course for pc in path_courses]).values_list('course_id', flat=True)
        
    return render(request, 'courses/student/path_detail.html', {
        'path': path,
        'path_courses': path_courses,
        'enrolled_course_ids': enrolled_course_ids
    })


def landing_page(request):
    if request.user.is_authenticated:
        return redirect_based_on_role(request.user)
    courses = Course.objects.filter(status='published').order_by('-created_at')[:3]
    return render(request, 'landing.html', {'featured_courses': courses})

def certificate_view(request, course_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    
    if enrollment.progress_percentage < 100:
        messages.error(request, 'Anda belum menyelesaikan kursus ini sepenuhnya.')
        return redirect('student_course_detail', course_id=course.id)
        
    from .models import Certificate
    certificate, _ = Certificate.objects.get_or_create(enrollment=enrollment)
    
    return render(request, 'certificate.html', {
        'certificate': certificate,
        'course': course,
        'student': request.user
    })

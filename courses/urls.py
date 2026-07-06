from django.urls import path
from . import views, api_views

urlpatterns = [
    # Public & Auth
    path('', views.landing_page, name='landing_page'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('impersonate/<int:user_id>/', views.impersonate_user, name='impersonate_user'),

    # Admin Command Center
    path('admin-command/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-command/site-settings/', views.admin_site_settings, name='admin_site_settings'),
    path('admin-command/course/<int:course_id>/review/', views.review_course, name='review_course'),
    path('admin-command/course/<int:course_id>/edit/', views.admin_course_edit, name='admin_course_edit'),
    path('admin-command/course/<int:course_id>/delete/', views.admin_course_delete, name='admin_course_delete'),
    
    # Admin Categories
    path('admin-command/categories/', views.admin_categories, name='admin_categories'),
    path('admin-command/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('admin-command/categories/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('admin-command/categories/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),
    
    # Admin Users
    path('admin-command/users/', views.admin_users, name='admin_users'),
    path('admin-command/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin-command/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin-command/users/<int:user_id>/reset-password/', views.admin_user_reset_password, name='admin_user_reset_password'),
    path('admin-command/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),

    # Instructor Panel
    path('instructor-panel/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor-panel/course/create/', views.create_course, name='create_course'),
    path('instructor-panel/course/<int:course_id>/request-review/', views.request_course_review, name='request_course_review'),
    path('instructor-panel/course/<int:course_id>/csv-upload/', views.csv_upload_students, name='csv_upload_students'),
    path('instructor-panel/course/<int:course_id>/export-grades/', views.export_course_grades, name='export_course_grades'),
    path('instructor-panel/course/<int:course_id>/manage/', views.instructor_course_manage, name='instructor_course_manage'),
    path('instructor-panel/course/<int:course_id>/delete/', views.instructor_course_delete, name='instructor_course_delete'),
    path('instructor-panel/course/<int:course_id>/section/add/', views.instructor_section_create, name='instructor_section_create'),
    path('instructor-panel/section/<int:section_id>/lesson/add/', views.instructor_lesson_create, name='instructor_lesson_create'),
    path('instructor-panel/course/<int:course_id>/announcement/add/', views.instructor_announcement_create, name='instructor_announcement_create'),
    path('instructor-panel/course/<int:course_id>/quiz/add/', views.instructor_quiz_create, name='instructor_quiz_create'),
    path('instructor-panel/lesson/<int:lesson_id>/assignment/add/', views.instructor_assignment_create, name='instructor_assignment_create'),
    path('api/instructor/lessons/reorder/', views.api_reorder_lessons, name='api_reorder_lessons'),

    path('profile/', views.user_profile, name='user_profile'),
    path('profile/password/', views.user_password_change, name='user_password_change'),
    
    # Student Space
    path('student-space/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student-space/catalog/', views.student_catalog, name='student_catalog'),
    path('student-space/course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('student-space/course/<int:course_id>/', views.student_course_detail, name='student_course_detail'),
    path('student-space/course/<int:course_id>/certificate/', views.certificate_view, name='certificate_view'),
    path('student-space/lesson/<int:lesson_id>/', views.take_lesson, name='take_lesson'),
    path('student-space/quiz/<int:bank_id>/submit/', views.submit_quiz_ajax, name='submit_quiz_ajax'),

    # Learning Paths
    path('learning-paths/', views.learning_paths_list, name='learning_paths_list'),
    path('learning-paths/<slug:slug>/', views.learning_path_detail, name='learning_path_detail'),

    # API Endpoints for Postman Testing
    # Auth
    path('api/auth/register', api_views.api_register, name='api_register'),
    path('api/auth/login', api_views.api_login, name='api_login'),
    
    # Public
    path('api/categories', api_views.api_get_categories, name='api_get_categories'),
    path('api/courses', api_views.api_get_courses, name='api_get_courses'),
    path('api/courses/<int:course_id>', api_views.api_get_course_detail, name='api_get_course_detail'),
    
    # Student
    path('api/courses/<int:course_id>/enroll', api_views.api_enroll_course, name='api_enroll_course'),
    path('api/student/dashboard', api_views.api_student_dashboard, name='api_student_dashboard'),
    path('api/student/lesson/<int:lesson_id>/complete', api_views.api_mark_lesson_complete, name='api_mark_lesson_complete'),
    path('api/learning-paths', api_views.api_get_learning_paths, name='api_get_learning_paths'),
    path('api/learning-paths/<int:path_id>', api_views.api_get_path_detail, name='api_get_path_detail'),
    path('api/profile/update', api_views.api_update_profile, name='api_update_profile'),
    
    # Instructor
    path('api/instructor/stats', api_views.api_instructor_stats, name='api_instructor_stats'),
    path('api/instructor/courses', api_views.api_instructor_courses, name='api_instructor_courses'),
    path('api/instructor/courses/create', api_views.api_instructor_create_course, name='api_instructor_create_course'),
    path('api/instructor/courses/<int:course_id>/delete', api_views.api_instructor_delete_course, name='api_instructor_delete_course'),
    path('api/instructor/courses/<int:course_id>/sections', api_views.api_instructor_create_section, name='api_instructor_create_section'),
    path('api/instructor/courses/<int:course_id>/announcements', api_views.api_instructor_create_announcement, name='api_instructor_create_announcement'),
    path('api/instructor/sections/<int:section_id>/lessons', api_views.api_instructor_create_lesson, name='api_instructor_create_lesson'),
    path('api/instructor/lessons/<int:lesson_id>/assignments', api_views.api_instructor_create_assignment, name='api_instructor_create_assignment'),
    
    # Admin
    path('api/admin/stats', api_views.api_admin_stats, name='api_admin_stats'),
    path('api/admin/users', api_views.api_admin_users, name='api_admin_users'),
    path('api/admin/users/create', api_views.api_admin_user_create, name='api_admin_user_create'),
    path('api/admin/users/<int:user_id>/delete', api_views.api_admin_user_delete, name='api_admin_user_delete'),
    path('api/admin/courses/<int:course_id>/review', api_views.api_admin_review_course, name='api_admin_review_course'),
    path('api/admin/categories/create', api_views.api_admin_category_create, name='api_admin_category_create'),
    path('api/admin/categories/<int:category_id>/delete', api_views.api_admin_category_delete, name='api_admin_category_delete'),
]
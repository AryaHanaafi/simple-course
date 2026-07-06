from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import uuid

class User(AbstractUser):
    ROLES = (
        ('superadmin', 'Super Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='student')

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class SiteSetting(models.Model):
    site_name = models.CharField(max_length=100, default="NextGen Pro Learning")
    announcement_banner = models.TextField(blank=True, null=True, help_text="Displays at the top of every page if active.")
    is_banner_active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.site_name

class Course(models.Model):
    DIFFICULTY_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('published', 'Published'),
    )
    
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    FORMAT_CHOICES = (
        ('video', 'Video URL/Embed'),
        ('text', 'Rich Text/Article'),
        ('file', 'File Attachment'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    )
    
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content_format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='text')
    content = models.TextField(blank=True, help_text="Rich text content or Video Embed/URL")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Prerequisite(models.Model):
    # A prerequisite can be another course or a lesson
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='prerequisites', null=True, blank=True)
    required_course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='lesson_prerequisites', null=True, blank=True)
    required_lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)

class QuestionBank(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='question_banks')
    title = models.CharField(max_length=255)
    
    def __str__(self):
        return self.title

class MultipleChoice(models.Model):
    question_bank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])

    def __str__(self):
        return self.question_text[:50]

class Assignment(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='assignment')
    title = models.CharField(max_length=255)
    instructions = models.TextField()
    max_score = models.FloatField(default=100.0)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('student', 'course')

    @property
    def progress_percentage(self):
        total_lessons = Lesson.objects.filter(section__course=self.course).count()
        if total_lessons == 0:
            return 0
        completed = self.progress_records.filter(is_completed=True).count()
        return round((completed / total_lessons) * 100, 2)

class Progress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='progress_records')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('enrollment', 'lesson')

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    file_submission = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('assignment', 'student')

class QuizAttempt(models.Model):
    question_bank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)
    attempted_at = models.DateTimeField(auto_now_add=True)

class LearningPath(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class LearningPathCourse(models.Model):
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='path_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.learning_path.title} - {self.course.title} (Step {self.order})"

class CourseAnnouncement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class LessonComment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.lesson.title}"

class Certificate(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'Certificate for {self.enrollment.student.username}'

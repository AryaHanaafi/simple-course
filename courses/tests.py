from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Course, Section, Lesson, Prerequisite, QuestionBank, MultipleChoice, Enrollment, Progress
import json
from django.core.cache import cache

class NextGenProTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.student = User.objects.create_user(username='student1', password='pw', role='student')
        self.instructor = User.objects.create_user(username='instructor1', password='pw', role='instructor')
        self.admin = User.objects.create_user(username='admin1', password='pw', role='superadmin')
        
        # Create course
        self.course = Course.objects.create(title="Python 101", slug="python-101", difficulty="beginner", status="published", instructor=self.instructor)
        self.course_advanced = Course.objects.create(title="Python 201", slug="python-201", difficulty="advanced", status="published", instructor=self.instructor)
        
        # Sections & Lessons
        self.section = Section.objects.create(course=self.course, title="Basics", order=1)
        self.lesson1 = Lesson.objects.create(section=self.section, title="Intro", order=1)
        self.lesson2 = Lesson.objects.create(section=self.section, title="Variables", order=2)
        
        # Prerequisite
        Prerequisite.objects.create(lesson=self.lesson2, required_lesson=self.lesson1)
        
        # Question Bank & MCQs
        self.bank = QuestionBank.objects.create(course=self.course, title="Quiz 1")
        self.q1 = MultipleChoice.objects.create(question_bank=self.bank, question_text="What is 1+1?", option_a="1", option_b="2", option_c="3", option_d="4", correct_option="B")

    # 1. Role Protection Test
    def test_role_protection(self):
        self.client.login(username='student1', password='pw')
        # Student trying to access instructor panel
        response = self.client.get(reverse('instructor_dashboard'))
        self.assertEqual(response.status_code, 403) # PermissionDenied
        
        self.client.login(username='instructor1', password='pw')
        response = self.client.get(reverse('instructor_dashboard'))
        self.assertEqual(response.status_code, 200)

    # 2. Filtering & Pagination Test
    def test_catalog_filtering_pagination(self):
        self.client.login(username='student1', password='pw')
        
        # Test difficulty filter
        response = self.client.get(reverse('student_catalog') + '?difficulty=advanced')
        self.assertContains(response, "Python 201")
        self.assertNotContains(response, "Python 101")
        
        # Test search filter
        response = self.client.get(reverse('student_catalog') + '?q=101')
        self.assertContains(response, "Python 101")
        self.assertNotContains(response, "Python 201")

    # 3. Custom Throttling Middleware Test
    def test_login_throttling(self):
        # Clear cache first
        cache.clear()
        
        for i in range(5):
            response = self.client.post(reverse('login'), {'username': 'wrong', 'password': 'pw'}, REMOTE_ADDR='127.0.0.1')
            self.assertEqual(response.status_code, 200) # Re-renders login page due to invalid creds
            
        # 6th attempt should be blocked (403 Forbidden)
        response = self.client.post(reverse('login'), {'username': 'wrong', 'password': 'pw'}, REMOTE_ADDR='127.0.0.1')
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Rate limit exceeded", status_code=403)

    # 4. Content Dripping Test
    def test_content_dripping(self):
        self.client.login(username='student1', password='pw')
        Enrollment.objects.create(student=self.student, course=self.course)
        
        # Trying to access lesson 2 without completing lesson 1
        response = self.client.get(reverse('take_lesson', args=[self.lesson2.id]))
        self.assertContains(response, "You must complete a previous lesson first.")
        
        # Complete lesson 1
        enrollment = Enrollment.objects.get(student=self.student, course=self.course)
        Progress.objects.create(enrollment=enrollment, lesson=self.lesson1, is_completed=True)
        
        # Now access lesson 2
        response = self.client.get(reverse('take_lesson', args=[self.lesson2.id]))
        self.assertEqual(response.status_code, 200) # Can access now

    # 5. Auto Grading Logic Test
    def test_auto_grading_ajax(self):
        self.client.login(username='student1', password='pw')
        
        data = {
            'answers': {
                str(self.q1.id): 'B' # Correct answer
            }
        }
        
        response = self.client.post(
            reverse('submit_quiz_ajax', args=[self.bank.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        resp_data = json.loads(response.content)
        self.assertEqual(resp_data['score'], 100.0)
        self.assertEqual(resp_data['correct_count'], 1)

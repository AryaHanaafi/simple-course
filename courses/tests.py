from django.test import TestCase, Client
from django.urls import reverse
from courses.models import User, Course, Category

class APIUnitTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test category
        self.category = Category.objects.create(
            name="Programming",
            slug="programming",
            description="Programming courses"
        )
        
        # Create a test instructor
        self.instructor = User.objects.create_user(
            username="test_instructor",
            password="testpassword",
            email="instructor@test.com",
            role="instructor"
        )
        
        # Create a test student
        self.student = User.objects.create_user(
            username="test_student",
            password="testpassword",
            email="student@test.com",
            role="student"
        )
        
        # Create a published course
        self.course = Course.objects.create(
            title="Test Course",
            slug="test-course",
            instructor=self.instructor,
            category=self.category,
            status="published",
            difficulty="beginner"
        )

    def test_get_categories_api(self):
        """Test the public categories API endpoint"""
        response = self.client.get(reverse('api_get_categories'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(len(data['data']) >= 1)
        self.assertEqual(data['data'][0]['name'], 'Programming')

    def test_get_courses_api_with_pagination_and_filtering(self):
        """Test the public courses API with pagination and filtering"""
        # Test basic get
        response = self.client.get(reverse('api_get_courses'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 1)
        
        # Test pagination
        response = self.client.get(reverse('api_get_courses') + '?page=1&limit=10')
        data = response.json()
        self.assertIn('pagination', data)
        self.assertEqual(data['pagination']['total_items'], 1)
        
        # Test filtering
        response = self.client.get(reverse('api_get_courses') + '?search=Test')
        data = response.json()
        self.assertEqual(len(data['data']), 1)
        
        response = self.client.get(reverse('api_get_courses') + '?search=NotFoundXYZ')
        data = response.json()
        self.assertEqual(len(data['data']), 0)

    def test_auth_login_api(self):
        """Test the API login endpoint"""
        # Test invalid login
        response = self.client.post(
            reverse('api_login'), 
            data='{"username": "test_student", "password": "wrongpassword"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        
        # Test valid login
        response = self.client.post(
            reverse('api_login'), 
            data='{"username": "test_student", "password": "testpassword"}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['role'], 'student')

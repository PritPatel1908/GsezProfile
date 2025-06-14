from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

# Create your tests here.

class HomeViewTest(TestCase):
    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_system/home.html')

class UserRegistrationTest(TestCase):
    def test_registration_form_display(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_system/register.html')
    
    def test_registration_form_submission(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'complex_password123',
            'password2': 'complex_password123',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'testuser')

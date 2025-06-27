from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm


class UserModelTests(TestCase):
    """
    Test cases for User and UserProfile models.
    """
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_profile_creation(self):
        """Test that UserProfile is created automatically when User is created."""
        self.assertTrue(hasattr(self.user, 'userprofile'))
        self.assertIsInstance(self.user.userprofile, UserProfile)
    
    def test_user_profile_str(self):
        """Test UserProfile string representation."""
        expected = f"{self.user.username}'s Profile"
        self.assertEqual(str(self.user.userprofile), expected)


class UserFormsTests(TestCase):
    """
    Test cases for user forms.
    """
    
    def test_user_registration_form_valid(self):
        """Test valid user registration form."""
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_user_registration_form_invalid_email(self):
        """Test user registration form with invalid email."""
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'invalid-email',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class UserViewsTests(TestCase):
    """
    Test cases for user views.
    """
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_register_view_get(self):
        """Test GET request to register view."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')
    
    def test_login_view_get(self):
        """Test GET request to login view."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome Back')
    
    def test_profile_view_requires_login(self):
        """Test that profile view requires authentication."""
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, '/login/?next=/profile/')
    
    def test_dashboard_view_requires_login(self):
        """Test that dashboard view requires authentication."""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/login/?next=/dashboard/')
    
    def test_profile_view_authenticated(self):
        """Test profile view with authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Update Profile')
    
    def test_dashboard_view_authenticated(self):
        """Test dashboard view with authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
    
    def test_user_registration_post(self):
        """Test user registration via POST."""
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertRedirects(response, reverse('login'))
        
        # Check that user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Check that profile was created
        user = User.objects.get(username='newuser')
        self.assertTrue(hasattr(user, 'userprofile'))
    
    def test_user_login_post(self):
        """Test user login via POST."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        }, follow=True)
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_user_logout(self):
        """Test user logout."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

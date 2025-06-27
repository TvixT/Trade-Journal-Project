from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from journal.models import Trade
from decimal import Decimal
from django.utils import timezone

class HomepageTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_homepage_anonymous_user(self):
        """Test homepage for anonymous users."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Trading Journal')
        self.assertContains(response, 'Master the markets')
        self.assertContains(response, 'Start Trading')
        self.assertContains(response, 'Login')

    def test_homepage_authenticated_user(self):
        """Test homepage for authenticated users."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome back, testuser')
        self.assertContains(response, 'View Dashboard')
        self.assertContains(response, 'Add Trade')

    def test_homepage_with_trades(self):
        """Test homepage with user trades for market sentiment."""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a profitable trade for bull sentiment
        Trade.objects.create(
            user=self.user,
            symbol='EURUSD',
            position_type='LONG',
            position_size=Decimal('100000'),
            entry_price=Decimal('1.1000'),
            exit_price=Decimal('1.1100'),
            asset_type='FOREX',
            is_open=False,
            entry_date=timezone.now()
        )
        
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'bull-mode')
        self.assertContains(response, '1')  # Total trades

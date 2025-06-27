from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from journal.models import Trade
from journal.templatetags.journal_extras import total_risk_amount, total_reward_amount
from django.utils import timezone

class TemplateFiltersTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_total_risk_amount_long_position(self):
        """Test total risk amount calculation for LONG position."""
        trade = Trade.objects.create(
            user=self.user,
            symbol='EURUSD',
            position_type='LONG',
            position_size=Decimal('100000'),  # 100k units
            entry_price=Decimal('1.1000'),
            stop_loss=Decimal('1.0950'),     # 50 pips risk
            take_profit=Decimal('1.1100'),   # 100 pips reward  
            asset_type='FOREX',
            entry_date=timezone.now()
        )
        
        # Risk should be: (1.1000 - 1.0950) * 100000 = 0.0050 * 100000 = 500
        expected_risk = Decimal('500.00')
        actual_risk = total_risk_amount(trade)
        self.assertEqual(actual_risk, expected_risk)

    def test_total_reward_amount_long_position(self):
        """Test total reward amount calculation for LONG position."""
        trade = Trade.objects.create(
            user=self.user,
            symbol='EURUSD',
            position_type='LONG',
            position_size=Decimal('100000'),  # 100k units
            entry_price=Decimal('1.1000'),
            stop_loss=Decimal('1.0950'),     # 50 pips risk
            take_profit=Decimal('1.1100'),   # 100 pips reward
            asset_type='FOREX',
            entry_date=timezone.now()
        )
        
        # Reward should be: (1.1100 - 1.1000) * 100000 = 0.0100 * 100000 = 1000
        expected_reward = Decimal('1000.00')
        actual_reward = total_reward_amount(trade)
        self.assertEqual(actual_reward, expected_reward)

    def test_total_risk_amount_short_position(self):
        """Test total risk amount calculation for SHORT position."""
        trade = Trade.objects.create(
            user=self.user,
            symbol='EURUSD',
            position_type='SHORT',
            position_size=Decimal('50000'),   # 50k units
            entry_price=Decimal('1.1000'),
            stop_loss=Decimal('1.1050'),     # 50 pips risk
            take_profit=Decimal('1.0900'),   # 100 pips reward
            asset_type='FOREX',
            entry_date=timezone.now()
        )
        
        # Risk should be: (1.1050 - 1.1000) * 50000 = 0.0050 * 50000 = 250
        expected_risk = Decimal('250.00')
        actual_risk = total_risk_amount(trade)
        self.assertEqual(actual_risk, expected_risk)

    def test_total_reward_amount_short_position(self):
        """Test total reward amount calculation for SHORT position."""
        trade = Trade.objects.create(
            user=self.user,
            symbol='EURUSD', 
            position_type='SHORT',
            position_size=Decimal('50000'),   # 50k units
            entry_price=Decimal('1.1000'),
            stop_loss=Decimal('1.1050'),     # 50 pips risk
            take_profit=Decimal('1.0900'),   # 100 pips reward
            asset_type='FOREX',
            entry_date=timezone.now()
        )
        
        # Reward should be: (1.1000 - 1.0900) * 50000 = 0.0100 * 50000 = 500
        expected_reward = Decimal('500.00')
        actual_reward = total_reward_amount(trade)
        self.assertEqual(actual_reward, expected_reward)

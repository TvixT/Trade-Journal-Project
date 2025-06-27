from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Trade, JournalEntry
from datetime import datetime
from django.test import TestCase

User = get_user_model()

class TradeJournalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user2 = User.objects.create_user(username='otheruser', password='otherpass')
        self.trade = Trade.objects.create(
            user=self.user,
            symbol='AAPL',
            asset_type='STOCK',
            entry_price=100.0,
            exit_price=110.0,
            position_size=10,
            entry_date=datetime.now(),
            position_type='LONG',
            is_open=False
        )
        self.journal_entry = JournalEntry.objects.create(
            user=self.user,
            trade=self.trade,
            title='First Entry',
            content='This is a test journal entry.',
            entry_date=datetime.now()
        )

    def test_trade_list_view_requires_login(self):
        response = self.client.get(reverse('trade_list'))
        self.assertNotEqual(response.status_code, 200)
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('trade_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AAPL')

    def test_trade_create_and_update(self):
        self.client.login(username='testuser', password='testpass')
        trade_data = {
            'symbol': 'GOOG',
            'asset_type': 'STOCK',
            'position_type': 'LONG',
            'entry_price': '200.0',
            'position_size': '5',
            'entry_date': '2025-06-26T12:00',
            'is_open': 'on',  # Checkbox field sends 'on' when checked
            'commission': '0.00',
            'notes': ''
        }
        response = self.client.post(reverse('trade_create'), trade_data, follow=True)
        # Check if trade was created
        self.assertTrue(Trade.objects.filter(user=self.user, symbol='GOOG').exists())
        trade = Trade.objects.get(user=self.user, symbol='GOOG')
        
        # Test update
        update_data = {
            'symbol': 'GOOG',
            'asset_type': 'STOCK',
            'position_type': 'LONG',
            'entry_price': '210.0',
            'position_size': '5',
            'entry_date': '2025-06-26T12:00',
            'is_open': 'on',
            'commission': '0.00',
            'notes': ''
        }
        response = self.client.post(reverse('trade_update', args=[trade.pk]), update_data, follow=True)
        trade.refresh_from_db()
        self.assertEqual(float(trade.entry_price), 210.0)

    def test_trade_delete(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('trade_delete', args=[self.trade.pk]))
        self.assertFalse(Trade.objects.filter(pk=self.trade.pk).exists())

    def test_journal_entry_crud(self):
        self.client.login(username='testuser', password='testpass')
        # Create
        response = self.client.post(reverse('journal_create'), {
            'trade': self.trade.pk,
            'title': 'Second Entry',
            'content': 'Another entry.',
            'entry_date': datetime.now().date().strftime('%Y-%m-%d')
        })
        self.assertEqual(JournalEntry.objects.filter(user=self.user, title='Second Entry').count(), 1)
        entry = JournalEntry.objects.get(user=self.user, title='Second Entry')
        # Update
        response = self.client.post(reverse('journal_update', args=[entry.pk]), {
            'trade': self.trade.pk,
            'title': 'Second Entry Updated',
            'content': 'Updated content.',
            'entry_date': entry.entry_date.strftime('%Y-%m-%d')
        })
        entry.refresh_from_db()
        self.assertEqual(entry.title, 'Second Entry Updated')
        # Delete
        response = self.client.post(reverse('journal_delete', args=[entry.pk]))
        self.assertFalse(JournalEntry.objects.filter(pk=entry.pk).exists())

    def test_user_cannot_access_others_trades(self):
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.get(reverse('trade_detail', args=[self.trade.pk]))
        self.assertEqual(response.status_code, 403)

    def test_user_cannot_access_others_journal_entries(self):
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.get(reverse('journal_detail', args=[self.journal_entry.pk]))
        self.assertEqual(response.status_code, 403)

#!/usr/bin/env python
"""
Script to add sample trading data for dashboard testing
"""

import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_journal.settings')
django.setup()

from django.contrib.auth.models import User
from journal.models import Trade, JournalEntry

def create_sample_data():
    """Create sample trading data for testing the dashboard"""
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created user: {user.username}")
    
    # Clear existing data for this user
    Trade.objects.filter(user=user).delete()
    JournalEntry.objects.filter(user=user).delete()
    
    # Sample trades data
    sample_trades = [
        # Winning trades
        {
            'symbol': 'AAPL',
            'position_type': 'LONG',
            'entry_price': Decimal('150.00'),
            'exit_price': Decimal('155.00'),
            'position_size': 100,
            'asset_type': 'stock',
            'entry_date': datetime.now() - timedelta(days=25),
            'exit_date': datetime.now() - timedelta(days=24),
            'is_open': False,
            'stop_loss': Decimal('145.00'),
            'take_profit': Decimal('160.00'),
        },
        {
            'symbol': 'TSLA',
            'position_type': 'LONG',
            'entry_price': Decimal('200.00'),
            'exit_price': Decimal('220.00'),
            'position_size': 50,
            'asset_type': 'stock',
            'entry_date': datetime.now() - timedelta(days=20),
            'exit_date': datetime.now() - timedelta(days=19),
            'is_open': False,
            'stop_loss': Decimal('190.00'),
            'take_profit': Decimal('230.00'),
        },
        # Losing trades
        {
            'symbol': 'MSFT',
            'position_type': 'LONG',
            'entry_price': Decimal('300.00'),
            'exit_price': Decimal('290.00'),
            'position_size': 25,
            'asset_type': 'stock',
            'entry_date': datetime.now() - timedelta(days=18),
            'exit_date': datetime.now() - timedelta(days=17),
            'is_open': False,
            'stop_loss': Decimal('285.00'),
            'take_profit': Decimal('320.00'),
        },
        {
            'symbol': 'GOOGL',
            'position_type': 'SHORT',
            'entry_price': Decimal('2500.00'),
            'exit_price': Decimal('2550.00'),
            'position_size': 10,
            'asset_type': 'stock',
            'entry_date': datetime.now() - timedelta(days=15),
            'exit_date': datetime.now() - timedelta(days=14),
            'is_open': False,
            'stop_loss': Decimal('2580.00'),
            'take_profit': Decimal('2400.00'),
        },
        # More winning trades
        {
            'symbol': 'BTC/USD',
            'position_type': 'LONG',
            'entry_price': Decimal('45000.00'),
            'exit_price': Decimal('48000.00'),
            'position_size': Decimal('0.5'),
            'asset_type': 'crypto',
            'entry_date': datetime.now() - timedelta(days=12),
            'exit_date': datetime.now() - timedelta(days=11),
            'is_open': False,
            'stop_loss': Decimal('42000.00'),
            'take_profit': Decimal('50000.00'),
        },
        {
            'symbol': 'ETH/USD',
            'position_type': 'LONG',
            'entry_price': Decimal('3200.00'),
            'exit_price': Decimal('3400.00'),
            'position_size': 5,
            'asset_type': 'crypto',
            'entry_date': datetime.now() - timedelta(days=10),
            'exit_date': datetime.now() - timedelta(days=9),
            'is_open': False,
            'stop_loss': Decimal('3000.00'),
            'take_profit': Decimal('3600.00'),
        },
        # Open trades
        {
            'symbol': 'NVDA',
            'position_type': 'LONG',
            'entry_price': Decimal('400.00'),
            'position_size': 30,
            'asset_type': 'stock',
            'entry_date': datetime.now() - timedelta(days=5),
            'is_open': True,
            'stop_loss': Decimal('380.00'),
            'take_profit': Decimal('450.00'),
        },
        {
            'symbol': 'EUR/USD',
            'position_type': 'SHORT',
            'entry_price': Decimal('1.1200'),
            'position_size': 10000,
            'asset_type': 'forex',
            'entry_date': datetime.now() - timedelta(days=3),
            'is_open': True,
            'stop_loss': Decimal('1.1250'),
            'take_profit': Decimal('1.1100'),
        },
        # Recent winning trade
        {
            'symbol': 'AMD',
            'position_type': 'LONG',
            'entry_price': Decimal('120.00'),
            'exit_price': Decimal('130.00'),
            'position_size': 40,
            'asset_type': 'stock',
            'entry_date': datetime.now() - timedelta(days=2),
            'exit_date': datetime.now() - timedelta(days=1),
            'is_open': False,
            'stop_loss': Decimal('115.00'),
            'take_profit': Decimal('135.00'),
        },
    ]
    
    # Create trades
    created_trades = []
    for trade_data in sample_trades:
        trade = Trade.objects.create(user=user, **trade_data)
        created_trades.append(trade)
    
    print(f"Created {len(created_trades)} sample trades")
    
    # Create some journal entries
    journal_entries = [
        {
            'content': 'Great trade on AAPL today. Market was bullish and technical analysis was spot on.',
            'trade': created_trades[0],
            'rating': 5,
            'lessons_learned': 'Always trust the technical analysis when fundamentals align.',
            'entry_date': (datetime.now() - timedelta(days=24)).date(),
            'created_at': datetime.now() - timedelta(days=24, hours=2)
        },
        {
            'content': 'TSLA trade worked out well. Earnings beat expectations driving price higher.',
            'trade': created_trades[1],
            'rating': 4,
            'lessons_learned': 'Earnings plays can be profitable with proper risk management.',
            'entry_date': (datetime.now() - timedelta(days=19)).date(),
            'created_at': datetime.now() - timedelta(days=19, hours=1)
        },
        {
            'content': 'Should have stuck to my stop loss on MSFT. Market turned against me.',
            'trade': created_trades[2],
            'rating': 2,
            'lessons_learned': 'Never move stop losses against your position.',
            'entry_date': (datetime.now() - timedelta(days=17)).date(),
            'created_at': datetime.now() - timedelta(days=17, hours=3)
        },
        {
            'content': 'Crypto market is showing strength. BTC broke key resistance.',
            'trade': created_trades[4],
            'rating': 5,
            'lessons_learned': 'Crypto momentum trades can be very profitable.',
            'entry_date': (datetime.now() - timedelta(days=11)).date(),
            'created_at': datetime.now() - timedelta(days=11, hours=2)
        },
        {
            'content': 'General market analysis: Tech stocks showing resilience despite macro concerns.',
            'rating': 3,
            'lessons_learned': 'Keep an eye on sector rotation patterns.',
            'entry_date': (datetime.now() - timedelta(days=7)).date(),
            'created_at': datetime.now() - timedelta(days=7)
        }
    ]
    
    created_entries = []
    for entry_data in journal_entries:
        entry = JournalEntry.objects.create(user=user, **entry_data)
        created_entries.append(entry)
    
    print(f"Created {len(created_entries)} sample journal entries")
    
    # Print summary
    total_trades = Trade.objects.filter(user=user).count()
    winning_trades = sum(1 for t in Trade.objects.filter(user=user, is_open=False) if t.profit_loss > 0)
    total_pnl = sum(t.profit_loss for t in Trade.objects.filter(user=user, is_open=False))
    
    print(f"\nSample data summary for user '{user.username}':")
    print(f"Total trades: {total_trades}")
    print(f"Winning trades: {winning_trades}")
    print(f"Total P&L: ${total_pnl:.2f}")
    print(f"Total journal entries: {len(created_entries)}")

if __name__ == '__main__':
    create_sample_data()

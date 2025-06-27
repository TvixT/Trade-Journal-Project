#!/usr/bin/env python
"""
Create some test open trades with take profit and stop loss values.
"""
import os
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_journal.settings')
django.setup()

from journal.models import Trade
from django.contrib.auth.models import User
from django.utils import timezone

def main():
    print("=== Creating Test Open Trades ===")
    
    # Get a test user (assuming testuser exists)
    try:
        user = User.objects.get(username='testuser')
        print(f"Using user: {user.username}")
    except User.DoesNotExist:
        user = User.objects.first()
        print(f"Using first user: {user.username}")
    
    # Create some test trades with different scenarios
    test_trades = [
        {
            'symbol': 'AAPL',
            'entry_price': Decimal('150.00'),
            'take_profit': Decimal('160.00'),
            'stop_loss': Decimal('145.00'),
            'position_size': Decimal('100.00'),
        },
        {
            'symbol': 'TSLA',
            'entry_price': Decimal('200.00'),
            'take_profit': Decimal('220.00'),
            'stop_loss': None,  # No stop loss
            'position_size': Decimal('50.00'),
        },
        {
            'symbol': 'MSFT',
            'entry_price': Decimal('300.00'),
            'take_profit': None,  # No take profit
            'stop_loss': Decimal('290.00'),
            'position_size': Decimal('75.00'),
        },
        {
            'symbol': 'GOOGL',
            'entry_price': Decimal('120.00'),
            'take_profit': None,  # Neither TP nor SL
            'stop_loss': None,
            'position_size': Decimal('25.00'),
        }
    ]
    
    created_trades = []
    for trade_data in test_trades:
        trade = Trade.objects.create(
            user=user,
            symbol=trade_data['symbol'],
            asset_type='STOCK',
            position_type='LONG',
            entry_price=trade_data['entry_price'],
            take_profit=trade_data['take_profit'],
            stop_loss=trade_data['stop_loss'],
            position_size=trade_data['position_size'],
            entry_date=timezone.now(),
            commission=Decimal('5.00'),
            is_open=True,
            notes=f"Test trade for {trade_data['symbol']} - testing auto-fill functionality"
        )
        created_trades.append(trade)
        print(f"Created trade: {trade.symbol} (ID: {trade.pk})")
        print(f"  Entry: ${trade.entry_price}")
        print(f"  Take Profit: ${trade.take_profit or 'None'}")
        print(f"  Stop Loss: ${trade.stop_loss or 'None'}")
        print()
    
    print(f"Total open trades created: {len(created_trades)}")
    print("Now you can test the close trade functionality!")

if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""
Quick verification of sample data and calculations
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_journal.settings')
django.setup()

from django.contrib.auth.models import User
from journal.models import Trade

def verify_data():
    """Verify sample data calculations"""
    
    user = User.objects.get(username='testuser')
    trades = Trade.objects.filter(user=user)
    
    print(f"User: {user.username}")
    print(f"Total trades: {trades.count()}")
    print("\nTrade details:")
    
    for trade in trades:
        if trade.is_open:
            print(f"{trade.symbol}: OPEN - Entry: ${trade.entry_price}, Size: {trade.position_size}")
        else:
            pnl = trade.profit_loss
            print(f"{trade.symbol}: CLOSED - Entry: ${trade.entry_price}, Exit: ${trade.exit_price}, P&L: ${pnl:.2f}")
    
    # Calculate summary
    closed_trades = trades.filter(is_open=False)
    total_pnl = sum(trade.profit_loss for trade in closed_trades)
    winning_trades = sum(1 for trade in closed_trades if trade.profit_loss > 0)
    losing_trades = sum(1 for trade in closed_trades if trade.profit_loss < 0)
    
    print(f"\nSummary:")
    print(f"Closed trades: {closed_trades.count()}")
    print(f"Winning trades: {winning_trades}")
    print(f"Losing trades: {losing_trades}")
    print(f"Total P&L: ${total_pnl:.2f}")
    
    if closed_trades.count() > 0:
        win_rate = (winning_trades / closed_trades.count()) * 100
        print(f"Win rate: {win_rate:.1f}%")

if __name__ == '__main__':
    verify_data()

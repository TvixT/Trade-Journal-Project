#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_journal.settings')
django.setup()

from journal.models import Trade
from django.contrib.auth.models import User
from decimal import Decimal

# Get test user
try:
    user = User.objects.get(username='testuser')
    print(f"Found user: {user.username}")
    
    # Get all closed trades ordered by entry date
    closed_trades = Trade.objects.filter(user=user, is_open=False).order_by('entry_date')
    
    print(f"\nTotal closed trades: {closed_trades.count()}")
    print("\nTrade sequence (chronological order):")
    print("Date       | Symbol | P&L      | Result")
    print("-" * 40)
    
    # Calculate consecutive wins/losses correctly
    max_consecutive_wins = 0
    max_consecutive_losses = 0
    current_wins = 0
    current_losses = 0
    
    for i, trade in enumerate(closed_trades, 1):
        pnl = trade.profit_loss
        result = "WIN" if pnl > 0 else "LOSS" if pnl < 0 else "BREAKEVEN"
        
        print(f"{trade.entry_date.strftime('%Y-%m-%d')} | {trade.symbol:6} | ${pnl:8.2f} | {result}")
        
        # Count consecutive wins/losses
        if pnl > 0:
            current_wins += 1
            current_losses = 0
            max_consecutive_wins = max(max_consecutive_wins, current_wins)
            print(f"                                    -> Current win streak: {current_wins}")
        elif pnl < 0:
            current_losses += 1
            current_wins = 0
            max_consecutive_losses = max(max_consecutive_losses, current_losses)
            print(f"                                    -> Current loss streak: {current_losses}")
        else:  # Break-even trade
            current_wins = 0
            current_losses = 0
            print(f"                                    -> Streak reset (breakeven)")
    
    print(f"\nFinal Results:")
    print(f"Max consecutive wins: {max_consecutive_wins}")
    print(f"Max consecutive losses: {max_consecutive_losses}")
    
except User.DoesNotExist:
    print("Test user not found")
except Exception as e:
    print(f"Error: {e}")

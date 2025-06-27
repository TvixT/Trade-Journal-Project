#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_journal.settings')
django.setup()

from journal.models import Trade
from django.contrib.auth.models import User

# Get test user
try:
    user = User.objects.get(username='testuser')
    print(f"Found user: {user.username}")
    
    # Get ALL trades (open and closed) ordered by entry date
    all_trades = Trade.objects.filter(user=user).order_by('entry_date')
    
    print(f"\nAll trades (including open): {all_trades.count()}")
    print("\nTrade sequence (chronological order):")
    print("Date       | Symbol | P&L      | Status   | Result")
    print("-" * 50)
    
    for trade in all_trades:
        status = "OPEN" if trade.is_open else "CLOSED"
        pnl = trade.profit_loss if not trade.is_open else "N/A (Open)"
        
        if trade.is_open:
            result = "PENDING"
        else:
            result = "WIN" if trade.profit_loss > 0 else "LOSS" if trade.profit_loss < 0 else "BREAKEVEN"
        
        print(f"{trade.entry_date.strftime('%Y-%m-%d')} | {trade.symbol:6} | {str(pnl):8} | {status:7} | {result}")
    
    # Also check if there might be different users
    print(f"\nAll users in system:")
    for u in User.objects.all():
        trade_count = Trade.objects.filter(user=u).count()
        print(f"  {u.username}: {trade_count} trades")

except User.DoesNotExist:
    print("Test user not found")
except Exception as e:
    print(f"Error: {e}")

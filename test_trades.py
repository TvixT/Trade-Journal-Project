#!/usr/bin/env python
"""
Quick script to check current trades and their status.
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_journal.settings')
django.setup()

from journal.models import Trade
from django.contrib.auth.models import User

def main():
    print("=== Trade Status Check ===")
    
    # Get all users
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    
    for user in users:
        print(f"\nUser: {user.username}")
        trades = Trade.objects.filter(user=user)
        print(f"Total trades: {trades.count()}")
        
        open_trades = trades.filter(is_open=True)
        closed_trades = trades.filter(is_open=False)
        
        print(f"Open trades: {open_trades.count()}")
        print(f"Closed trades: {closed_trades.count()}")
        
        if open_trades.exists():
            print("\nOpen trades details:")
            for trade in open_trades[:5]:  # Show first 5
                print(f"  ID: {trade.pk}, Symbol: {trade.symbol}, Entry: ${trade.entry_price}, TP: ${trade.take_profit or 'None'}, SL: ${trade.stop_loss or 'None'}")
        
        if closed_trades.exists():
            print(f"\nRecent closed trades: {closed_trades.count()}")
            for trade in closed_trades.order_by('-exit_date')[:3]:  # Show last 3 closed
                print(f"  ID: {trade.pk}, Symbol: {trade.symbol}, Exit: ${trade.exit_price}, Reason: {trade.exit_reason}")

if __name__ == '__main__':
    main()

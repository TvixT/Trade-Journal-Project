#!/usr/bin/env python
"""
Debug position types and calculations
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_journal.settings')
django.setup()

from django.contrib.auth.models import User
from journal.models import Trade

def debug_calculations():
    """Debug the profit loss calculations"""
    
    user = User.objects.get(username='testuser')
    trades = Trade.objects.filter(user=user, is_open=False)
    
    print("Debugging profit/loss calculations:")
    print("=" * 50)
    
    for trade in trades:
        print(f"\nTrade: {trade.symbol}")
        print(f"Position Type: '{trade.position_type}'")
        print(f"Entry Price: ${trade.entry_price}")
        print(f"Exit Price: ${trade.exit_price}")
        print(f"Position Size: {trade.position_size}")
        print(f"Commission: ${trade.commission}")
        
        # Manual calculation
        if trade.position_type == 'LONG':
            manual_pnl = (trade.exit_price - trade.entry_price) * trade.position_size - trade.commission
        else:
            manual_pnl = (trade.entry_price - trade.exit_price) * trade.position_size - trade.commission
        
        print(f"Manual P&L calculation: ${manual_pnl:.2f}")
        print(f"Model P&L property: ${trade.profit_loss:.2f}")
        print(f"Match: {manual_pnl == trade.profit_loss}")

if __name__ == '__main__':
    debug_calculations()

#!/usr/bin/env python
"""
Test script to verify lot size calculations and P&L are working correctly.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_journal.settings')
django.setup()

from journal.models import Trade
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime

def test_lot_calculations():
    print("=== Testing Lot Size Calculations ===\n")
    
    # Create a test user
    try:
        user = User.objects.get(username='test_user')
    except User.DoesNotExist:
        user = User.objects.create_user(username='test_user', password='test123')
    
    # Test cases for different asset types
    test_cases = [
        {
            'name': 'Forex Standard Lot',
            'asset_type': 'FOREX',
            'position_size': Decimal('100000'),  # 100,000 units
            'expected_lots': Decimal('1.0000'),
            'entry_price': Decimal('1.2000'),
            'exit_price': Decimal('1.2100'),
            'expected_pnl': Decimal('1000.00')  # (1.21 - 1.20) * 100000 = 1000
        },
        {
            'name': 'Forex Mini Lot',
            'asset_type': 'FOREX',
            'position_size': Decimal('10000'),  # 10,000 units
            'expected_lots': Decimal('0.1000'),
            'entry_price': Decimal('1.2000'),
            'exit_price': Decimal('1.2100'),
            'expected_pnl': Decimal('100.00')  # (1.21 - 1.20) * 10000 = 100
        },
        {
            'name': 'Stock Round Lot',
            'asset_type': 'STOCK',
            'position_size': Decimal('100'),  # 100 shares
            'expected_lots': Decimal('1.0000'),
            'entry_price': Decimal('100.00'),
            'exit_price': Decimal('105.00'),
            'expected_pnl': Decimal('500.00')  # (105 - 100) * 100 = 500
        },
        {
            'name': 'Oil Contract',
            'asset_type': 'OIL',
            'position_size': Decimal('1000'),  # 1000 barrels
            'expected_lots': Decimal('1.0000'),
            'entry_price': Decimal('70.00'),
            'exit_price': Decimal('72.00'),
            'expected_pnl': Decimal('2000.00')  # (72 - 70) * 1000 = 2000
        },
        {
            'name': 'Commodity (Gold)',
            'asset_type': 'COMMODITY',
            'position_size': Decimal('100'),  # 100 troy ounces
            'expected_lots': Decimal('1.0000'),
            'entry_price': Decimal('2000.00'),
            'exit_price': Decimal('2050.00'),
            'expected_pnl': Decimal('5000.00')  # (2050 - 2000) * 100 = 5000
        },
        {
            'name': 'Cryptocurrency',
            'asset_type': 'CRYPTO',
            'position_size': Decimal('0.5'),  # 0.5 Bitcoin
            'expected_lots': Decimal('0.5000'),
            'entry_price': Decimal('50000.00'),
            'exit_price': Decimal('52000.00'),
            'expected_pnl': Decimal('1000.00')  # (52000 - 50000) * 0.5 = 1000
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. {case['name']}")
        
        # Create trade
        trade = Trade.objects.create(
            user=user,
            symbol=f"TEST{i}",
            asset_type=case['asset_type'],
            position_type='LONG',
            entry_price=case['entry_price'],
            exit_price=case['exit_price'],
            position_size=case['position_size'],
            entry_date=datetime.now(),
            is_open=False,
            commission=Decimal('0.00')
        )
        
        # Test lot size calculation
        calculated_lots = trade.lot_size
        print(f"   Position Size: {trade.position_size} units")
        print(f"   Expected Lots: {case['expected_lots']}")
        print(f"   Calculated Lots: {calculated_lots}")
        print(f"   Lot Size ✓" if abs(calculated_lots - case['expected_lots']) < Decimal('0.0001') else f"   Lot Size ✗")
        
        # Test P&L calculation
        calculated_pnl = trade.profit_loss
        print(f"   Expected P&L: ${case['expected_pnl']}")
        print(f"   Calculated P&L: ${calculated_pnl}")
        print(f"   P&L ✓" if abs(calculated_pnl - case['expected_pnl']) < Decimal('0.01') else f"   P&L ✗")
        print()
        
        # Clean up
        trade.delete()
    
    # Clean up user
    user.delete()
    
    print("=== Test Complete ===")

if __name__ == '__main__':
    test_lot_calculations()

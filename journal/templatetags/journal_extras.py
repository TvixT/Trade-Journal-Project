from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def subtract(value, arg):
    """Subtract arg from value"""
    try:
        return Decimal(str(value)) - Decimal(str(arg))
    except (ValueError, TypeError, InvalidOperation):
        return 0

@register.filter
def abs_value(value):
    """Return absolute value"""
    try:
        return abs(Decimal(str(value)))
    except (ValueError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError, InvalidOperation):
        return 0

@register.filter
def total_risk_amount(trade):
    """Calculate total risk amount based on position type"""
    if not trade.stop_loss:
        return Decimal('0')
    
    try:
        if trade.position_type == 'LONG':
            risk_per_unit = abs(trade.entry_price - trade.stop_loss)
        else:  # SHORT
            risk_per_unit = abs(trade.stop_loss - trade.entry_price)
        
        return risk_per_unit * trade.position_size
    except (ValueError, TypeError, AttributeError):
        return Decimal('0')

@register.filter
def total_reward_amount(trade):
    """Calculate total reward amount based on position type"""
    if not trade.take_profit:
        return Decimal('0')
    
    try:
        if trade.position_type == 'LONG':
            reward_per_unit = abs(trade.take_profit - trade.entry_price)
        else:  # SHORT
            reward_per_unit = abs(trade.entry_price - trade.take_profit)
        
        return reward_per_unit * trade.position_size
    except (ValueError, TypeError, AttributeError):
        return Decimal('0')

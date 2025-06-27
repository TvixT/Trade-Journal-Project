from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from journal.models import Trade
from decimal import Decimal
import random

def homepage(request):
    """Homepage with bear/bull market theme."""
    context = {}
    
    if request.user.is_authenticated:
        # Get user's trading stats for personalized experience
        trades = Trade.objects.filter(user=request.user)
        total_trades = trades.count()
        
        # Calculate total P&L by iterating through trades
        total_pnl = Decimal('0')
        for trade in trades:
            total_pnl += trade.profit_loss
        
        # Determine market sentiment based on recent P&L
        recent_trades = trades.order_by('-entry_date')[:5]
        recent_pnl = sum(trade.profit_loss for trade in recent_trades) if recent_trades else Decimal('0')
        
        if total_pnl > 0 or recent_pnl > 0:
            market_sentiment = 'bull'
        elif total_pnl < 0 or recent_pnl < 0:
            market_sentiment = 'bear'
        else:
            market_sentiment = 'neutral'
            
        context.update({
            'total_trades': total_trades,
            'total_pnl': total_pnl,
            'market_sentiment': market_sentiment,
            'recent_trades': recent_trades,
        })
    else:
        # For anonymous users, show random market sentiment
        context['market_sentiment'] = random.choice(['bull', 'bear', 'neutral'])
    
    return render(request, 'homepage.html', context)

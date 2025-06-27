from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm


class CustomLoginView(LoginView):
    """
    Custom login view with additional template context.
    """
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('journal_dashboard')


class CustomLogoutView(LogoutView):
    """
    Custom logout view.
    """
    next_page = 'login'


class RegisterView(CreateView):
    """
    User registration view.
    """
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        """Handle valid form submission."""
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        messages.success(self.request, f'Account created for {username}! You can now log in.')
        return response


@login_required
def profile_view(request):
    """
    User profile view and update functionality.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered profile template with forms
    """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.userprofile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.userprofile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Profile'
    }
    return render(request, 'users/profile.html', context)


@login_required
def dashboard_view(request):
    """
    Enhanced dashboard view with comprehensive trading KPIs and analytics, supporting time-based filtering.
    """
    from journal.models import Trade, JournalEntry
    from django.db.models import Sum, Count, Q, F, Avg
    from decimal import Decimal
    import json
    from datetime import datetime, timedelta
    from django.utils import timezone

    # --- Time Filter Logic ---
    time_filter = request.GET.get('time_filter', 'all')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    now = timezone.now()
    trades = Trade.objects.filter(user=request.user)

    # Determine date range based on filter
    if time_filter == 'last_month':
        first_of_this_month = now.replace(day=1)
        last_month_end = first_of_this_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        trades = trades.filter(entry_date__gte=last_month_start, entry_date__lte=last_month_end)
    elif time_filter == 'this_month':
        first_of_this_month = now.replace(day=1)
        trades = trades.filter(entry_date__gte=first_of_this_month)
    elif time_filter == 'custom' and start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            trades = trades.filter(entry_date__date__gte=start, entry_date__date__lte=end)
        except Exception:
            pass  # fallback to all if invalid
    # else: 'all' - no date filter

    closed_trades = trades.filter(is_open=False)
    open_trades = trades.filter(is_open=True)
    total_trades = trades.count()

    # Calculate total P&L and individual trade P&Ls
    total_pnl = Decimal('0.00')
    winning_trades = 0
    losing_trades = 0
    profitable_trades = []
    losing_trade_amounts = []

    for trade in closed_trades:
        pnl = trade.profit_loss
        total_pnl += pnl
        if pnl > 0:
            winning_trades += 1
            profitable_trades.append(float(pnl))
        elif pnl < 0:
            losing_trades += 1
            losing_trade_amounts.append(float(abs(pnl)))

    win_rate = 0
    if closed_trades.count() > 0:
        win_rate = round((winning_trades / closed_trades.count()) * 100, 1)

    avg_profit = Decimal('0.00')
    avg_loss = Decimal('0.00')
    if profitable_trades:
        avg_profit = Decimal(str(sum(profitable_trades) / len(profitable_trades)))
    if losing_trade_amounts:
        avg_loss = Decimal(str(sum(losing_trade_amounts) / len(losing_trade_amounts)))

    total_rr = Decimal('0.00')
    rr_count = 0
    for trade in closed_trades:
        if trade.risk_reward_ratio > 0:
            total_rr += trade.risk_reward_ratio
            rr_count += 1
    avg_rr = round(float(total_rr / rr_count), 2) if rr_count > 0 else 0.00

    max_consecutive_wins = 0
    max_consecutive_losses = 0
    current_wins = 0
    current_losses = 0
    for trade in closed_trades.order_by('entry_date'):
        if trade.profit_loss > 0:
            current_wins += 1
            current_losses = 0
            max_consecutive_wins = max(max_consecutive_wins, current_wins)
        elif trade.profit_loss < 0:
            current_losses += 1
            current_wins = 0
            max_consecutive_losses = max(max_consecutive_losses, current_losses)
        else:
            current_wins = 0
            current_losses = 0

    # --- P&L over time data for selected period ---
    period_trades = closed_trades.order_by('entry_date')
    pnl_dates = []
    pnl_values = []
    cumulative_pnl = Decimal('0.00')
    for trade in period_trades:
        cumulative_pnl += trade.profit_loss
        pnl_dates.append(trade.entry_date.strftime('%Y-%m-%d'))
        pnl_values.append(float(cumulative_pnl))

    profit_loss_data = {
        'profitable': len(profitable_trades),
        'losing': len(losing_trade_amounts),
        'breakeven': closed_trades.count() - len(profitable_trades) - len(losing_trade_amounts)
    }

    asset_distribution = {}
    for trade in trades:
        asset_type = trade.get_asset_type_display()
        asset_distribution[asset_type] = asset_distribution.get(asset_type, 0) + 1

    # Recent trades and journal entries (not filtered by time period)
    recent_trades_activity = Trade.objects.filter(user=request.user).order_by('-entry_date')[:5]
    recent_journal_entries = JournalEntry.objects.filter(user=request.user).order_by('-created_at')[:3]

    context = {
        'title': 'Trading Dashboard',
        'user': request.user,
        'total_trades': total_trades,
        'total_pnl': total_pnl,
        'win_rate': win_rate,
        'avg_profit': avg_profit,
        'avg_loss': avg_loss,
        'avg_rr': avg_rr,
        'max_consecutive_wins': max_consecutive_wins,
        'max_consecutive_losses': max_consecutive_losses,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'open_trades_count': open_trades.count(),
        'pnl_chart_data': json.dumps({'dates': pnl_dates, 'values': pnl_values}),
        'profit_loss_distribution': json.dumps(profit_loss_data),
        'asset_distribution': json.dumps(asset_distribution),
        'recent_trades': recent_trades_activity,
        'recent_journal_entries': recent_journal_entries,
        'has_trades': total_trades > 0,
        'has_journal_entries': recent_journal_entries.exists(),
        'time_filter': time_filter,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'users/dashboard.html', context)

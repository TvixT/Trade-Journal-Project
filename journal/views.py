from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count, Avg, Case, When, DecimalField, F
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal
import logging
from .models import Trade, JournalEntry
from .forms import TradeForm, JournalEntryForm, TradeFilterForm, JournalFilterForm
from .position_size_forms import PositionSizeCalculatorForm
from .forum_models import ForumThread, ForumPost, NewsArticle
from .forum_forms import ForumThreadForm, ForumPostForm
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


# Dashboard View
@login_required
def journal_dashboard(request):
    """
    Main dashboard for journal functionality with statistics.
    Redirects to the enhanced dashboard in users app.
    
    Args:
        request: HTTP request object
        
    Returns:
        Redirect to enhanced dashboard
    """
    from django.shortcuts import redirect
    return redirect('dashboard')


# Trade Views
class TradeListView(LoginRequiredMixin, ListView):
    """List view for user's trades with filtering."""
    model = Trade
    template_name = 'journal/trade_list.html'
    context_object_name = 'trades'
    paginate_by = 10

    def get_queryset(self):
        """Filter trades for current user and apply search filters."""
        queryset = Trade.objects.filter(user=self.request.user)
        
        # Apply filters
        form = TradeFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data['symbol']:
                queryset = queryset.filter(symbol__icontains=form.cleaned_data['symbol'])
            if form.cleaned_data['position_type']:
                queryset = queryset.filter(position_type=form.cleaned_data['position_type'])
            if form.cleaned_data['status']:
                status = form.cleaned_data['status']
                if status == 'open':
                    queryset = queryset.filter(is_open=True)
                elif status == 'win':
                    # Closed trades with positive P&L
                    # Calculate P&L for LONG: (exit_price - entry_price) * position_size - commission
                    # Calculate P&L for SHORT: (entry_price - exit_price) * position_size - commission
                    queryset = queryset.filter(
                        is_open=False,
                        exit_price__isnull=False
                    ).annotate(
                        calculated_pnl=Case(
                            When(position_type='LONG', then=(F('exit_price') - F('entry_price')) * F('position_size') - F('commission')),
                            When(position_type='SHORT', then=(F('entry_price') - F('exit_price')) * F('position_size') - F('commission')),
                            output_field=DecimalField(max_digits=12, decimal_places=2)
                        )
                    ).filter(calculated_pnl__gt=0)
                elif status == 'loss':
                    # Closed trades with negative P&L
                    queryset = queryset.filter(
                        is_open=False,
                        exit_price__isnull=False
                    ).annotate(
                        calculated_pnl=Case(
                            When(position_type='LONG', then=(F('exit_price') - F('entry_price')) * F('position_size') - F('commission')),
                            When(position_type='SHORT', then=(F('entry_price') - F('exit_price')) * F('position_size') - F('commission')),
                            output_field=DecimalField(max_digits=12, decimal_places=2)
                        )
                    ).filter(calculated_pnl__lt=0)
                elif status == 'breakeven':
                    # Closed trades with zero P&L
                    queryset = queryset.filter(
                        is_open=False,
                        exit_price__isnull=False
                    ).annotate(
                        calculated_pnl=Case(
                            When(position_type='LONG', then=(F('exit_price') - F('entry_price')) * F('position_size') - F('commission')),
                            When(position_type='SHORT', then=(F('entry_price') - F('exit_price')) * F('position_size') - F('commission')),
                            output_field=DecimalField(max_digits=12, decimal_places=2)
                        )
                    ).filter(calculated_pnl=0)
            if form.cleaned_data['date_from']:
                queryset = queryset.filter(entry_date__date__gte=form.cleaned_data['date_from'])
            if form.cleaned_data['date_to']:
                queryset = queryset.filter(entry_date__date__lte=form.cleaned_data['date_to'])
        
        return queryset

    def get_context_data(self, **kwargs):
        """Add filter form to context."""
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TradeFilterForm(self.request.GET)
        context['title'] = 'My Trades'
        
        # Create query string for pagination (excluding page parameter)
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['query_string'] = query_params.urlencode()
        
        return context


class TradeDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a single trade."""
    model = Trade
    template_name = 'journal/trade_detail.html'
    context_object_name = 'trade'

    def test_func(self):
        """Ensure user can only view their own trades."""
        trade = self.get_object()
        return trade.user == self.request.user

    def get_context_data(self, **kwargs):
        """Add related journal entries to context."""
        context = super().get_context_data(**kwargs)
        context['journal_entries'] = self.object.journal_entries.all()
        context['title'] = f'Trade: {self.object.symbol}'
        return context


class TradeCreateView(LoginRequiredMixin, CreateView):
    """Create view for new trades."""
    model = Trade
    form_class = TradeForm
    template_name = 'journal/trade_form.html'
    success_url = reverse_lazy('journal_dashboard')

    def form_valid(self, form):
        """Set user before saving."""
        form.instance.user = self.request.user
        messages.success(self.request, 'Trade created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Trade'
        context['button_text'] = 'Create Trade'
        return context


class TradeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update view for existing trades."""
    model = Trade
    form_class = TradeForm
    template_name = 'journal/trade_form.html'
    success_url = reverse_lazy('journal_dashboard')

    def test_func(self):
        """Ensure user can only edit their own trades."""
        trade = self.get_object()
        return trade.user == self.request.user

    def form_valid(self, form):
        """Add success message."""
        messages.success(self.request, 'Trade updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Trade: {self.object.symbol}'
        context['button_text'] = 'Update Trade'
        return context


class TradeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete view for trades."""
    model = Trade
    template_name = 'journal/trade_confirm_delete.html'
    success_url = reverse_lazy('journal_dashboard')

    def test_func(self):
        """Ensure user can only delete their own trades."""
        trade = self.get_object()
        return trade.user == self.request.user

    def delete(self, request, *args, **kwargs):
        """Add success message on deletion."""
        messages.success(self.request, 'Trade deleted successfully!')
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Trade: {self.object.symbol}'
        return context


# Journal Entry Views
class JournalEntryListView(LoginRequiredMixin, ListView):
    """List view for user's journal entries with filtering."""
    model = JournalEntry
    template_name = 'journal/journal_list.html'
    context_object_name = 'entries'
    paginate_by = 10

    def get_queryset(self):
        """Filter journal entries for current user and apply search filters."""
        queryset = JournalEntry.objects.filter(user=self.request.user)
        
        # Apply filters
        form = JournalFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data['search']:
                search_term = form.cleaned_data['search']
                queryset = queryset.filter(
                    Q(title__icontains=search_term) |
                    Q(content__icontains=search_term) |
                    Q(tags__icontains=search_term)
                )
            if form.cleaned_data['mood']:
                queryset = queryset.filter(mood=form.cleaned_data['mood'])
            if form.cleaned_data['rating']:
                queryset = queryset.filter(rating=form.cleaned_data['rating'])
            if form.cleaned_data['date_from']:
                queryset = queryset.filter(entry_date__gte=form.cleaned_data['date_from'])
            if form.cleaned_data['date_to']:
                queryset = queryset.filter(entry_date__lte=form.cleaned_data['date_to'])
        
        return queryset

    def get_context_data(self, **kwargs):
        """Add filter form to context."""
        context = super().get_context_data(**kwargs)
        context['filter_form'] = JournalFilterForm(self.request.GET)
        context['title'] = 'Journal Entries'
        return context


class JournalEntryDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Detail view for a single journal entry."""
    model = JournalEntry
    template_name = 'journal/journal_detail.html'
    context_object_name = 'entry'

    def test_func(self):
        """Ensure user can only view their own journal entries."""
        entry = self.get_object()
        return entry.user == self.request.user

    def get_context_data(self, **kwargs):
        """Add title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        return context


class JournalEntryCreateView(LoginRequiredMixin, CreateView):
    """Create view for new journal entries."""
    model = JournalEntry
    form_class = JournalEntryForm
    template_name = 'journal/journal_form.html'
    success_url = reverse_lazy('journal_dashboard')

    def get_form_kwargs(self):
        """Pass user to form."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Set user before saving."""
        form.instance.user = self.request.user
        messages.success(self.request, 'Journal entry created successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'New Journal Entry'
        context['button_text'] = 'Create Entry'
        return context


class JournalEntryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update view for existing journal entries."""
    model = JournalEntry
    form_class = JournalEntryForm
    template_name = 'journal/journal_form.html'
    success_url = reverse_lazy('journal_dashboard')

    def test_func(self):
        """Ensure user can only edit their own journal entries."""
        entry = self.get_object()
        return entry.user == self.request.user

    def get_form_kwargs(self):
        """Pass user to form."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Add success message."""
        messages.success(self.request, 'Journal entry updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit: {self.object.title}'
        context['button_text'] = 'Update Entry'
        return context


class JournalEntryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete view for journal entries."""
    model = JournalEntry
    template_name = 'journal/journal_confirm_delete.html'
    success_url = reverse_lazy('journal_dashboard')

    def test_func(self):
        """Ensure user can only delete their own journal entries."""
        entry = self.get_object()
        return entry.user == self.request.user

    def delete(self, request, *args, **kwargs):
        """Add success message on deletion."""
        messages.success(self.request, 'Journal entry deleted successfully!')
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add title to context."""
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete: {self.object.title}'
        return context


# API Views for AJAX functionality
@login_required
def trade_stats_api(request):
    """
    API endpoint for trade statistics (for dashboard charts).
    
    Args:
        request: HTTP request object
        
    Returns:
        JsonResponse with trading statistics
    """
    user_trades = Trade.objects.filter(user=request.user, is_open=False)
    
    # Monthly P&L data
    monthly_pnl = {}
    for trade in user_trades:
        month_key = trade.entry_date.strftime('%Y-%m')
        if month_key not in monthly_pnl:
            monthly_pnl[month_key] = 0
        monthly_pnl[month_key] += float(trade.profit_loss)
    
    # Symbol distribution
    symbol_counts = {}
    for trade in user_trades:
        symbol_counts[trade.symbol] = symbol_counts.get(trade.symbol, 0) + 1
    
    return JsonResponse({
        'monthly_pnl': monthly_pnl,
        'symbol_distribution': symbol_counts,
        'total_trades': user_trades.count()
    })


@login_required
def close_trade(request, pk):
    """
    Close an open trade via AJAX.
    
    Args:
        request: HTTP request object
        pk: Primary key of the trade to close
        
    Returns:
        JsonResponse with success/error status
    """
    logger.info(f"Close trade request received for trade {pk} by user {request.user.username}")
    
    if request.method == 'POST':
        try:
            trade = get_object_or_404(Trade, pk=pk, user=request.user)
            logger.info(f"Trade found: {trade.symbol}, is_open: {trade.is_open}")
            
            if not trade.is_open:
                logger.warning(f"Attempt to close already closed trade {pk}")
                return JsonResponse({'success': False, 'error': 'Trade is already closed'})
            
            exit_price = request.POST.get('exit_price')
            exit_reason = request.POST.get('exit_reason', 'MANUAL')
            logger.info(f"Exit price: {exit_price}, Exit reason: {exit_reason}")
            
            if not exit_price:
                return JsonResponse({'success': False, 'error': 'Exit price is required'})
            
            try:
                exit_price_decimal = Decimal(str(exit_price))
                if exit_price_decimal <= 0:
                    return JsonResponse({'success': False, 'error': 'Exit price must be positive'})
                
                logger.info(f"Updating trade {pk} with exit price {exit_price_decimal}")
                trade.exit_price = exit_price_decimal
                trade.exit_reason = exit_reason
                trade.is_open = False
                trade.exit_date = timezone.now()
                trade.save()
                logger.info(f"Trade {pk} successfully closed")
                
                # Convert Decimal to float for JSON serialization
                profit_loss = trade.profit_loss
                profit_loss_percentage = trade.profit_loss_percentage
                logger.info(f"Calculated P&L: {profit_loss}, P&L%: {profit_loss_percentage}")
                
                return JsonResponse({
                    'success': True,
                    'profit_loss': float(profit_loss) if profit_loss else 0.0,
                    'profit_loss_percentage': float(profit_loss_percentage) if profit_loss_percentage else 0.0,
                    'exit_reason': trade.get_exit_reason_display()
                })
            except ValueError as ve:
                logger.error(f"ValueError in close_trade: {ve}")
                return JsonResponse({'success': False, 'error': f'Invalid exit price: {str(ve)}'})
            except Exception as e:
                logger.error(f"Exception saving trade {pk}: {e}")
                return JsonResponse({'success': False, 'error': f'Error saving trade: {str(e)}'})
                
        except Exception as e:
            logger.error(f"Exception in close_trade for trade {pk}: {e}")
            return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# Position Size Calculator View
@login_required
def position_size_calculator(request):
    result = None
    error = None
    if request.method == 'POST':
        form = PositionSizeCalculatorForm(request.POST)
        if form.is_valid():
            account_balance = form.cleaned_data['account_balance']
            risk_percent = form.cleaned_data['risk_percent']
            entry_price = form.cleaned_data['entry_price']
            stop_loss_price = form.cleaned_data['stop_loss_price']
            risk_amount = account_balance * (risk_percent / 100)
            price_diff = abs(entry_price - stop_loss_price)
            if price_diff > 0:
                position_size = risk_amount / price_diff
                result = round(position_size, 4)
            else:
                error = 'Entry price and stop loss price must not be equal.'
        else:
            error = 'Please correct the errors below.'
    else:
        form = PositionSizeCalculatorForm()
    return render(request, 'journal/position_size_calculator.html', {
        'form': form,
        'result': result,
        'error': error,
        'title': 'Position Size Calculator',
    })


# Forum Views
@login_required
def forum_list(request):
    threads = ForumThread.objects.order_by('-created_at')
    paginator = Paginator(threads, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'journal/forum_list.html', {'page_obj': page_obj, 'title': 'Trader Community Forum'})

@login_required
def forum_thread_detail(request, thread_id):
    thread = get_object_or_404(ForumThread, id=thread_id)
    posts = thread.posts.order_by('created_at')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post_form = ForumPostForm()
    if request.method == 'POST':
        post_form = ForumPostForm(request.POST)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post.thread = thread
            post.save()
            return redirect('forum_thread_detail', thread_id=thread.id)
    return render(request, 'journal/forum_thread_detail.html', {
        'thread': thread,
        'page_obj': page_obj,
        'post_form': post_form,
        'title': thread.title
    })

@login_required
def forum_new_thread(request):
    if request.method == 'POST':
        form = ForumThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.creator = request.user
            thread.save()
            # Optionally, create the first post if content is provided
            content = request.POST.get('content')
            if content:
                ForumPost.objects.create(thread=thread, author=request.user, content=content)
            return redirect('forum_thread_detail', thread_id=thread.id)
    else:
        form = ForumThreadForm()
    return render(request, 'journal/forum_new_thread.html', {'form': form, 'title': 'Start New Thread'})


# News Views
@login_required
def news_list(request):
    news_articles = []
    error = None
    MARKETAUX_API_KEY = getattr(settings, 'MARKETAUX_API_KEY', None)
    MARKETAUX_URL = 'https://api.marketaux.com/v1/news/all?filter_entities=true&language=en&api_token={}'

    logger.info(f"MARKETAUX_API_KEY present: {bool(MARKETAUX_API_KEY)}")
    try:
        if MARKETAUX_API_KEY:
            response = requests.get(MARKETAUX_URL.format(MARKETAUX_API_KEY), timeout=10)
            if response.status_code == 200:
                data = response.json()
                for article in data.get('data', []):
                    news_articles.append({
                        'title': article.get('title'),
                        'summary': article.get('description'),
                        'link': article.get('url'),
                        'published_at': article.get('published_at'),
                        'image_url': article.get('image_url'),
                    })
            else:
                error = f"Marketaux API error: {response.status_code}"
        else:
            error = "Marketaux API key not set."
    except Exception as e:
        logger.error(f"Marketaux API fetch error: {e}")
        error = "Could not fetch news from Marketaux."

    # Fallback to static news if no API key or error
    if not news_articles:
        try:
            news_articles = list(NewsArticle.objects.all().order_by('-published_at'))
            if not news_articles and not error:
                error = "No news articles available."
        except Exception as e:
            logger.error(f"Static news fetch error: {e}")
            if not error:
                error = "No news articles available."

    # Pagination
    paginator = Paginator(news_articles, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'journal/news_list.html', {
        'page_obj': page_obj,
        'error': error,
    })

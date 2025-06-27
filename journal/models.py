from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from decimal import Decimal


class Trade(models.Model):
    """
    Model representing a single trade entry.
    
    Attributes:
        user: ForeignKey to User who made the trade
        symbol: Stock/crypto symbol (e.g., AAPL, BTCUSD)
        position_type: Position type (LONG/SHORT) - Long = buying expecting price up, Short = selling expecting price down
        entry_price: Price at which position was entered
        exit_price: Price at which position was exited (nullable for open positions)
        position_size: Number of shares/units traded
        entry_date: Date and time when trade was entered
        exit_date: Date and time when trade was exited (nullable for open positions)
        stop_loss: Stop loss price (optional)
        take_profit: Take profit price (optional)
        commission: Commission/fees paid for the trade
        notes: Additional notes about the trade
        is_open: Whether the trade is still open
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    
    POSITION_TYPES = [
        ('LONG', 'Long'),
        ('SHORT', 'Short'),
    ]
    
    ASSET_TYPES = [
        ('FOREX', 'Forex'),
        ('STOCK', 'Stock/ETF'),
        ('COMMODITY', 'Commodity'),
        ('OIL', 'Oil'),
        ('CRYPTO', 'Cryptocurrency'),
    ]
    
    EXIT_REASONS = [
        ('MANUAL', 'Manual Close'),
        ('TAKE_PROFIT', 'Take Profit Hit'),
        ('STOP_LOSS', 'Stop Loss Hit'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trades')
    symbol = models.CharField(max_length=10, help_text="Stock/Crypto symbol (e.g., AAPL, BTCUSD)")
    asset_type = models.CharField(max_length=10, choices=ASSET_TYPES, default='FOREX', help_text="Type of asset being traded")
    position_type = models.CharField(max_length=5, choices=POSITION_TYPES, default='LONG', help_text="Long = Buy expecting price up, Short = Sell expecting price down")
    
    entry_price = models.DecimalField(
        max_digits=12, 
        decimal_places=4, 
        validators=[MinValueValidator(Decimal('0.0001'))],
        help_text="Price at which position was entered"
    )
    exit_price = models.DecimalField(
        max_digits=12, 
        decimal_places=4, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.0001'))],
        help_text="Price at which position was exited"
    )
    position_size = models.DecimalField(
        max_digits=12, 
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Number of units/shares traded (not lots). Examples: Forex: 10,000-100,000 units, Stocks: 100+ shares, Gold: 1-100 oz"
    )
    
    entry_date = models.DateTimeField(help_text="Date and time when trade was entered")
    exit_date = models.DateTimeField(null=True, blank=True, help_text="Date and time when trade was exited")
    exit_reason = models.CharField(
        max_length=15, 
        choices=EXIT_REASONS, 
        null=True, 
        blank=True,
        help_text="How the trade was closed"
    )
    
    stop_loss = models.DecimalField(
        max_digits=12, 
        decimal_places=4, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.0001'))],
        help_text="Stop loss price"
    )
    take_profit = models.DecimalField(
        max_digits=12, 
        decimal_places=4, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.0001'))],
        help_text="Take profit price"
    )
    commission = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Commission paid for the trade"
    )
    
    notes = models.TextField(blank=True, help_text="Additional notes about the trade")
    is_open = models.BooleanField(default=True, help_text="Whether the trade is still open")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-entry_date']
        verbose_name = 'Trade'
        verbose_name_plural = 'Trades'

    def __str__(self) -> str:
        """Return string representation of Trade."""
        status = "Open" if self.is_open else "Closed"
        return f"{self.symbol} - {self.position_type} - {status}"

    def get_absolute_url(self):
        """Return absolute URL for this trade."""
        return reverse('trade_detail', kwargs={'pk': self.pk})

    @property
    def profit_loss(self) -> Decimal:
        """
        Calculate profit/loss for the trade.
        
        Returns:
            Decimal: Profit (positive) or loss (negative) amount
        """
        if not self.exit_price:
            return Decimal('0.00')  # Open position
        
        if self.position_type == 'LONG':
            # Long position: profit when exit > entry
            return (self.exit_price - self.entry_price) * self.position_size - self.commission
        else:  # SHORT
            # Short position: profit when entry > exit
            return (self.entry_price - self.exit_price) * self.position_size - self.commission

    @property
    def profit_loss_percentage(self) -> Decimal:
        """
        Calculate profit/loss percentage.
        
        Returns:
            Decimal: Profit/loss as a percentage
        """
        if not self.exit_price or self.entry_price == 0:
            return Decimal('0.00')
        
        return (self.profit_loss / (self.entry_price * self.position_size)) * 100

    @property
    def total_value(self) -> Decimal:
        """
        Calculate total value of the position.
        
        Returns:
            Decimal: Total value of the position
        """
        return self.entry_price * self.position_size

    @property
    def risk_reward_ratio(self) -> Decimal:
        """
        Calculate Risk-Reward Ratio (RR).
        
        Returns:
            Decimal: Risk-Reward ratio. 
                    Risk = |entry_price - stop_loss|
                    Reward = |take_profit - entry_price|
                    RR = Reward / Risk
        """
        if not self.stop_loss or not self.take_profit:
            return Decimal('0.00')
        
        if self.position_type == 'LONG':
            # Long: Risk = entry - stop_loss, Reward = take_profit - entry
            risk = abs(self.entry_price - self.stop_loss)
            reward = abs(self.take_profit - self.entry_price)
        else:  # SHORT
            # Short: Risk = stop_loss - entry, Reward = entry - take_profit
            risk = abs(self.stop_loss - self.entry_price)
            reward = abs(self.entry_price - self.take_profit)
        
        if risk == 0:
            return Decimal('0.00')
        
        return reward / risk

    @property
    def unrealized_pnl(self) -> Decimal:
        """
        Calculate unrealized P&L for open positions using current market price.
        For demo purposes, this uses the take_profit as a proxy for current price.
        In a real app, you'd get live market data.
        
        Returns:
            Decimal: Unrealized profit/loss for open positions
        """
        if not self.is_open or not self.take_profit:
            return Decimal('0.00')
        
        # Using take_profit as proxy for current market price
        current_price = self.take_profit
        
        if self.position_type == 'LONG':
            return (current_price - self.entry_price) * self.position_size - self.commission
        else:  # SHORT
            return (self.entry_price - current_price) * self.position_size - self.commission

    @property
    def lot_size(self) -> Decimal:
        """
        Calculate lot size based on asset type and position size.
        
        Market Standards:
        - Forex: Standard Lot = 100,000 units, Mini Lot = 10,000 units, Micro Lot = 1,000 units
        - Stocks/ETFs: 1 lot = 100 shares (round lot)
        - Commodities: Varies (Oil = 1,000 barrels, Gold = 100 troy ounces, etc.)
        - Crypto: Not standardized, varies by exchange
        
        Returns:
            Decimal: Lot size (position_size / standard_lot_size)
        """
        if self.asset_type == 'FOREX':
            # Standard lot = 100,000 units
            return self.position_size / Decimal('100000')
        elif self.asset_type == 'OIL':
            # Oil: 1 lot = 1,000 barrels
            return self.position_size / Decimal('1000')
        elif self.asset_type == 'COMMODITY':
            # General commodities: varies, using 100 as default (like gold troy ounces)
            return self.position_size / Decimal('100')
        elif self.asset_type == 'STOCK':
            # Stocks: 1 round lot = 100 shares
            return self.position_size / Decimal('100')
        elif self.asset_type == 'CRYPTO':
            # Crypto: Not standardized, display as-is (1 unit = 1 "lot")
            return self.position_size
        else:
            # Default fallback (treat as forex)
            return self.position_size / Decimal('100000')

    @property
    def status(self) -> str:
        """
        Get the trade status based on position state and P&L.
        
        Returns:
            str: 'Open', 'Win', 'Loss', or 'Breakeven'
        """
        if self.is_open:
            return 'Open'
        
        pnl = self.profit_loss
        if pnl > 0:
            return 'Win'
        elif pnl < 0:
            return 'Loss'
        else:
            return 'Breakeven'


class JournalEntry(models.Model):
    """
    Model for detailed journal entries linked to trades.
    
    Attributes:
        user: ForeignKey to User who wrote the entry
        trade: ForeignKey to the associated Trade (optional)
        title: Title of the journal entry
        content: Detailed content of the journal entry
        entry_date: Date of the journal entry
        mood: Trader's mood during/after the trade
        market_conditions: Description of market conditions
        strategy_used: Trading strategy employed
        lessons_learned: What was learned from this trade
        tags: Comma-separated tags for categorization
        rating: Self-rating of trade execution (1-5)
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    
    MOOD_CHOICES = [
        ('CONFIDENT', 'Confident'),
        ('UNCERTAIN', 'Uncertain'),
        ('FEARFUL', 'Fearful'),
        ('GREEDY', 'Greedy'),
        ('CALM', 'Calm'),
        ('EXCITED', 'Excited'),
        ('FRUSTRATED', 'Frustrated'),
        ('DISCIPLINED', 'Disciplined'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journal_entries')
    trade = models.ForeignKey(
        Trade, 
        on_delete=models.CASCADE, 
        related_name='journal_entries',
        null=True,
        blank=True,
        help_text="Associated trade (optional)"
    )
    
    title = models.CharField(max_length=200, help_text="Title of the journal entry")
    content = models.TextField(help_text="Detailed content of the journal entry")
    entry_date = models.DateField(help_text="Date of the journal entry")
    
    mood = models.CharField(
        max_length=20, 
        choices=MOOD_CHOICES, 
        blank=True,
        help_text="Your mood during/after the trade"
    )
    market_conditions = models.TextField(
        blank=True,
        help_text="Description of market conditions"
    )
    strategy_used = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Trading strategy employed"
    )
    lessons_learned = models.TextField(
        blank=True,
        help_text="What was learned from this trade"
    )
    tags = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Comma-separated tags for categorization"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Self-rating of trade execution (1-5)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-entry_date', '-created_at']
        verbose_name = 'Journal Entry'
        verbose_name_plural = 'Journal Entries'

    def __str__(self) -> str:
        """Return string representation of JournalEntry."""
        return f"{self.title} - {self.entry_date}"

    def get_absolute_url(self):
        """Return absolute URL for this journal entry."""
        return reverse('journal_detail', kwargs={'pk': self.pk})

    @property
    def tag_list(self) -> list:
        """
        Return tags as a list.
        
        Returns:
            list: List of individual tags
        """
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    @property
    def rating_stars(self) -> str:
        """
        Return rating as star symbols.
        
        Returns:
            str: Star representation of rating
        """
        if not self.rating:
            return "Not rated"
        return "★" * self.rating + "☆" * (5 - self.rating)

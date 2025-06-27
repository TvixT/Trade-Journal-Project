from django.contrib import admin
from .models import Trade, JournalEntry


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    """
    Admin interface for Trade model.
    """
    list_display = ('symbol', 'user', 'position_type', 'entry_price', 'exit_price', 'profit_loss', 'is_open', 'entry_date')
    list_filter = ('position_type', 'is_open', 'entry_date', 'created_at')
    search_fields = ('symbol', 'user__username', 'user__email', 'notes')
    readonly_fields = ('profit_loss', 'profit_loss_percentage', 'total_value', 'created_at', 'updated_at')
    date_hierarchy = 'entry_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'symbol', 'position_type')
        }),
        ('Price & Size', {
            'fields': ('entry_price', 'exit_price', 'position_size', 'commission')
        }),
        ('Timing', {
            'fields': ('entry_date', 'exit_date', 'is_open')
        }),
        ('Risk Management', {
            'fields': ('stop_loss', 'take_profit')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Calculated Fields', {
            'fields': ('profit_loss', 'profit_loss_percentage', 'total_value'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def profit_loss(self, obj):
        """Display profit/loss in admin."""
        if obj.is_open:
            return "Open position"
        return f"${obj.profit_loss:.2f}"
    profit_loss.short_description = 'P&L'
    
    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request).select_related('user')


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    """
    Admin interface for JournalEntry model.
    """
    list_display = ('title', 'user', 'entry_date', 'mood', 'rating', 'trade', 'created_at')
    list_filter = ('mood', 'rating', 'entry_date', 'created_at')
    search_fields = ('title', 'content', 'user__username', 'user__email', 'tags', 'strategy_used')
    readonly_fields = ('tag_list', 'rating_stars', 'created_at', 'updated_at')
    date_hierarchy = 'entry_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'trade', 'title', 'entry_date')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Analysis', {
            'fields': ('mood', 'market_conditions', 'strategy_used', 'lessons_learned')
        }),
        ('Categorization', {
            'fields': ('tags', 'rating')
        }),
        ('Computed Fields', {
            'fields': ('tag_list', 'rating_stars'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request).select_related('user', 'trade')


# Custom admin site configuration
admin.site.site_header = "Trading Journal Administration"
admin.site.site_title = "Trading Journal Admin"
admin.site.index_title = "Welcome to Trading Journal Administration"

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.journal_dashboard, name='journal_dashboard'),
    
    # Trade URLs
    path('trades/', views.TradeListView.as_view(), name='trade_list'),
    path('trades/<int:pk>/', views.TradeDetailView.as_view(), name='trade_detail'),
    path('trades/add/', views.TradeCreateView.as_view(), name='trade_create'),
    path('trades/<int:pk>/edit/', views.TradeUpdateView.as_view(), name='trade_update'),
    path('trades/<int:pk>/delete/', views.TradeDeleteView.as_view(), name='trade_delete'),
    path('trades/<int:pk>/close/', views.close_trade, name='trade_close'),
    
    # Journal Entry URLs
    path('journal/', views.JournalEntryListView.as_view(), name='journal_list'),
    path('journal/<int:pk>/', views.JournalEntryDetailView.as_view(), name='journal_detail'),
    path('journal/add/', views.JournalEntryCreateView.as_view(), name='journal_create'),
    path('journal/<int:pk>/edit/', views.JournalEntryUpdateView.as_view(), name='journal_update'),
    path('journal/<int:pk>/delete/', views.JournalEntryDeleteView.as_view(), name='journal_delete'),
    
    # API URLs
    path('api/stats/', views.trade_stats_api, name='trade_stats_api'),

    # Position Size Calculator
    path('position-size-calculator/', views.position_size_calculator, name='position_size_calculator'),

    # Forum URLs
    path('forum/', views.forum_list, name='forum_list'),
    path('forum/thread/<int:thread_id>/', views.forum_thread_detail, name='forum_thread_detail'),
    path('forum/new/', views.forum_new_thread, name='forum_new_thread'),

    # News URLs
    path('news/', views.news_list, name='news_list'),
]
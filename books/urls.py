from django.urls import path
from .views import (BookListView, BookCreateView, BookDetailView, BookUpdateView, BookDeleteView,
                    ExchangeRequestListView, ExchangeRequestCreateView, ExchangeRequestDetailView,
                    ExchangeRequestUpdateView, ExchangeRequestDeleteView, DashboardBookListView)

urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),  # Get all books with filtering
    path('books/create/', BookCreateView.as_view(), name='book-create'),  # Create a new book
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),  # View details of a book
    path('books/<int:pk>/update/', BookUpdateView.as_view(), name='book-update'),  # Update a book
    path('books/<int:pk>/delete/', BookDeleteView.as_view(), name='book-delete'),  # Delete a book
    
    
    path('exchange-requests/', ExchangeRequestListView.as_view(), name='exchange-request-list'),
    path('exchange-requests/create/', ExchangeRequestCreateView.as_view(), name='exchange-request-create'),
    path('exchange-requests/<int:pk>/', ExchangeRequestDetailView.as_view(), name='exchange-request-detail'),
    path('exchange-requests/<int:pk>/update/', ExchangeRequestUpdateView.as_view(), name='exchange-request-update'),
    path('exchange-requests/<int:pk>/delete/', ExchangeRequestDeleteView.as_view(), name='exchange-request-delete'),
    path('dashboard/books/', DashboardBookListView.as_view(), name='dashboard-book-list'),
]

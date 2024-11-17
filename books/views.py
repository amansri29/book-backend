from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .models import Book
from .serializers import BookSerializer, BookCreateUpdateSerializer, ExchangeRequestReadSerializer
from django.db.models import Q

from rest_framework.pagination import PageNumberPagination

class BookListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: BookSerializer(many=True)},
    )
    def get(self, request):
        """
        List all books available for exchange, including filter options for title, author, genre, and availability.
        """
        books = Book.objects.filter(user=request.user)  # Only show books listed by the logged-in user
        # Search filters
        title = request.query_params.get('title', '')
        author = request.query_params.get('author', '')
        genre = request.query_params.get('genre', '')
        location = request.query_params.get('location', '')
        
        # Apply filters
        if title:
            books = books.filter(title__icontains=title)
        if author:
            books = books.filter(author__icontains=author)
        if genre:
            books = books.filter(genre__icontains=genre)
        if location:
            books = books.filter(location__icontains=location)

        # Return filtered books
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BookCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=BookCreateUpdateSerializer,
        responses={201: BookSerializer},
    )
    def post(self, request):
        """
        Add a new book to the user's exchange list.
        """
        serializer = BookCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Link the book to the current logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: BookSerializer},
    )
    def get(self, request, pk):
        """
        Get detailed information about a specific book.
        """
        try:
            book = Book.objects.get(pk=pk, user=request.user)
            serializer = BookSerializer(book)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

class BookUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=BookCreateUpdateSerializer,
        responses={200: BookSerializer},
    )
    def put(self, request, pk):
        """
        Update an existing book listing (e.g., title, author, genre, availability).
        """
        try:
            book = Book.objects.get(pk=pk, user=request.user)
            serializer = BookCreateUpdateSerializer(book, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

class BookDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={204: {"description": "Book deleted successfully."}},
    )
    def delete(self, request, pk):
        """
        Delete a specific book from the user's exchange list.
        """
        try:
            book = Book.objects.get(pk=pk, user=request.user)
            book.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)




from .models import ExchangeRequest, Book
from .serializers import ExchangeRequestSerializer

class ExchangeRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ExchangeRequestReadSerializer(many=True)},
    )
    def get(self, request):
        """
        List all exchange requests for the logged-in user (both incoming and outgoing).
        """
        incoming_requests = ExchangeRequest.objects.filter(receiver=request.user)
        outgoing_requests = ExchangeRequest.objects.filter(sender=request.user)
        exchange_requests = incoming_requests | outgoing_requests
        
        # Serialize the exchange requests and return
        serializer = ExchangeRequestReadSerializer(exchange_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExchangeRequestCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ExchangeRequestSerializer,
        responses={201: ExchangeRequestSerializer},
    )
    def post(self, request):
        """
        Send an exchange request to another user for a specific book.
        """
        book_id = request.data.get('book_id')
        receiver_id = request.data.get('receiver_id')
        delivery_method = request.data.get('delivery_method')
        exchange_duration = request.data.get('exchange_duration')
        

        # Validate that the user is not requesting their own book
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
        
       

        # Create exchange request
        exchange_request = ExchangeRequest.objects.create(
            sender=request.user,
            receiver_id=receiver_id,
            book=book,
            delivery_method=delivery_method,
            exchange_duration=exchange_duration,
        )

        # Return created exchange request
        serializer = ExchangeRequestSerializer(exchange_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExchangeRequestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ExchangeRequestSerializer},
    )
    def get(self, request, pk):
        """
        Get detailed information about a specific exchange request.
        """
        try:
            exchange_request = ExchangeRequest.objects.get(pk=pk)
            if exchange_request.sender != request.user and exchange_request.receiver != request.user:
                return Response({"error": "You are not authorized to view this request."}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = ExchangeRequestSerializer(exchange_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ExchangeRequest.DoesNotExist:
            return Response({"error": "Exchange request not found."}, status=status.HTTP_404_NOT_FOUND)


class ExchangeRequestUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ExchangeRequestSerializer,
        responses={200: ExchangeRequestSerializer},
    )
    def put(self, request, pk):
        """
        Update an existing exchange request (e.g., accept, reject, modify).
        """
        try:
            exchange_request = ExchangeRequest.objects.get(pk=pk)
            
            # Check if the logged-in user is the receiver
            if exchange_request.receiver != request.user:
                return Response({"error": "You can only update requests that were sent to you."}, status=status.HTTP_403_FORBIDDEN)

            # Update request status (accepted, rejected, modified)
            status = request.data.get('status')
            if status not in ['pending', 'accepted', 'rejected', 'modified']:
                return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)
            
            exchange_request.status = status
            exchange_request.save()

            # Return updated exchange request
            serializer = ExchangeRequestSerializer(exchange_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ExchangeRequest.DoesNotExist:
            return Response({"error": "Exchange request not found."}, status=status.HTTP_404_NOT_FOUND)


class ExchangeRequestDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={204: {"description": "Exchange request deleted successfully."}},
    )
    def delete(self, request, pk):
        """
        Delete a specific exchange request.
        """
        try:
            exchange_request = ExchangeRequest.objects.get(pk=pk)
            
            # Ensure the user is either the sender or the receiver
            if exchange_request.sender != request.user and exchange_request.receiver != request.user:
                return Response({"error": "You can only delete your own exchange requests."}, status=status.HTTP_403_FORBIDDEN)
            
            exchange_request.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ExchangeRequest.DoesNotExist:
            return Response({"error": "Exchange request not found."}, status=status.HTTP_404_NOT_FOUND)
        
        
        
class DashboardBookListView(APIView):
    permission_classes = [IsAuthenticated]

    class BookPagination(PageNumberPagination):
        page_size = 10  # Number of books per page
        page_size_query_param = 'page_size'
        max_page_size = 100

    @extend_schema(
        responses={200: BookSerializer(many=True)},
    )
    def get(self, request):
        """
        List all books available for exchange from all users, with search and pagination options.
        """
        books = Book.objects.all().order_by("-id")  # Fetch all books listed by users

        # Search filters (optional query parameters)
        title = request.query_params.get('title', '')
        author = request.query_params.get('author', '')
        genre = request.query_params.get('genre', '')
        location = request.query_params.get('location', '')

        # Apply filters based on query parameters
        if title:
            books = books.filter(title__icontains=title)
        if author:
            books = books.filter(author__icontains=author)
        if genre:
            books = books.filter(genre__icontains=genre)
        if location:
            books = books.filter(location__icontains=location)

        # Paginate the results
        paginator = self.BookPagination()
        paginated_books = paginator.paginate_queryset(books, request)

        # Serialize the books
        serializer = BookSerializer(paginated_books, many=True)

        # Return paginated response
        return paginator.get_paginated_response(serializer.data)
from rest_framework import serializers
from .models import Book, ExchangeRequest


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'condition', 'availability', 'location', 'user']

class BookCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'condition', 'availability', 'location']
        
        
# Exchange Request Serializer
class ExchangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRequest
        fields = '__all__'



# Exchange Request Serializer
class ExchangeRequestReadSerializer(serializers.ModelSerializer):
    book = BookSerializer()
    class Meta:
        model = ExchangeRequest
        fields = '__all__'
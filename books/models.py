from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    condition = models.CharField(max_length=50)
    availability = models.BooleanField(default=True)  # Whether the book is available or not
    location = models.CharField(max_length=255)
    user = models.ForeignKey(User, related_name='books', on_delete=models.CASCADE)  # Associate with user

    def __str__(self):
        return self.title
    
    
# Model to track exchange requests
class ExchangeRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('modified', 'Modified'),
    ]

    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='exchange_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    delivery_method = models.CharField(max_length=255)
    exchange_duration = models.IntegerField()  # in days
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Exchange request from {self.sender.username} to {self.receiver.username}"

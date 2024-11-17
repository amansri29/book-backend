from django.contrib import admin

from .models import Book, ExchangeRequest


# Register your models here.


admin.site.register(Book)
admin.site.register(ExchangeRequest)
from django.contrib import admin

# Register your models here.
from .models import Matching, Comment

admin.site.register(Matching)
admin.site.register(Comment)
from django.contrib import admin
from .models import Genre, Actor, Movie, Review
# Register your models here.

admin.site.register(Genre)
admin.site.register(Actor)
admin.site.register(Movie)
admin.site.register(Review)

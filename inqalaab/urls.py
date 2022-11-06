from django.contrib import admin
from django.urls import path, include

from .views import IndexClass, index_fun

urlpatterns = [
    path('class', IndexClass.as_view()),
    path('fun', index_fun),
]

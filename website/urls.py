from django.urls import path

from .views import IndexClass, index_fun

urlpatterns = [
    path('', index_fun),
    path('class', IndexClass.as_view()),
]

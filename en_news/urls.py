from django.urls import path
from .views import en_news_list

urlpatterns = [
    path('', en_news_list, name='en_news_list'),
]

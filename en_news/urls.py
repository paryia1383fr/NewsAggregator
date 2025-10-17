from django.urls import path
from .views import external_news_list

urlpatterns = [
    path('', external_news_list, name='external_news_list'),
]

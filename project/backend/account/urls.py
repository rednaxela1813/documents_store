from django.urls import path
from .views import RegisterUserView


app_name = 'account'

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    
]

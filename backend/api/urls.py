from django.urls import path
from .views import WindDataAPIView

urlpatterns = [
    path('wind-data/', WindDataAPIView.as_view(), name='wind-data'),
]
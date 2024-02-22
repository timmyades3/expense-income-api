from django.urls import path
from . import views

urlpatterns = [
    path('', views.IncomeListApiView.as_view(), name ='expenses'),
    path('<int:pk>/', views.IncomeDetailApiView.as_view(), name ='expenses detail')
]
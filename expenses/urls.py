from django.urls import path
from . import views

urlpatterns = [
    path('', views.ExpenseListApiView.as_view(), name ='expenses'),
    path('<int:pk>/', views.ExpenseDetailApiView.as_view(), name ='expenses detail')
]
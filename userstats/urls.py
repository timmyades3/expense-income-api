from django.urls import path
from . import views
urlpatterns = [
    path('expense_category_data', views.ExpenseSummaryStats.as_view(), name='expense-category-summary'),
    path('income_category_data', views.IncomeSummaryStats.as_view(), name='income-category-summary')
]
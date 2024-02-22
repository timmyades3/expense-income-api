from django.shortcuts import render
from rest_framework import generics,permissions,pagination
from .serializers import *
from .permissions import Isowner

# Create your views here.
class ExpenseListApiView(generics.ListCreateAPIView):
    serializer_class = ExpensesSerializer
    queryset = Expense.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class =  (pagination.PageNumberPagination)

    def perform_create(self, serializer):
        return serializer.save(owner =self.request.user)
    
    def get_quesryset(self):
        return self.queryset.filter(owner = self.request.user)
    

     
class ExpenseDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpensesSerializer
    queryset = Expense.objects.all()
    permission_classes = (permissions.IsAuthenticated,Isowner)
    lookup_fields = 'id'
    
    def get_quesryset(self):
        return self.queryset.filter(owner = self.request.user)
from django.shortcuts import render
from rest_framework.views import APIView
import datetime

# Create your views here.

class ExpenseSummaryStats(APIView):

    def get(self, request):
        todays_date = datetime.date.today()
        

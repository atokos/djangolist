from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def list_view(request):
    return HttpResponse("This is the index page")
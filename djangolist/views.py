from django.shortcuts import render
from django.http import HttpResponse

def welcome_view(response):
    return HttpResponse('This is the welcome page.')
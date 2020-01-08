from django.shortcuts import render
# from django.contrib import messages
# from django.views.generic import TemplateView


# Create your views here.
def landing(request):
    return render(request, "landing/landing.html")

from django.urls import path

from . import views

app_name='sliders'
urlpatterns = [
    path('', views.sliders, name='sliders'),
]

from django.urls import path

from . import views

app_name = 'gbm'
urlpatterns = [
    path('', views.gbm, name='gbm'),
]


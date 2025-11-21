from django.urls import path
from . import views

app_name = "leftovers"

urlpatterns = [
    path("input/", views.leftover_input, name="input"),
    path("recommend/", views.leftover_recommend, name="recommend"),
]

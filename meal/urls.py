from django.urls import path
from . import views

app_name = "meal"

urlpatterns = [
    path("quiz/", views.meal_quiz, name="quiz"),
    path("generate/", views.generate_meal_plan, name="generate"),
    path("plan/", views.view_meal_plan, name="plan"),
]
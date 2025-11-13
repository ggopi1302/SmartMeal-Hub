from django.urls import path
from . import views

app_name = "nutrition"

urlpatterns = [
    path("dashboard/", views.nutrition_dashboard, name="nutrition_dashboard"),
    path("add/<int:meal_id>/", views.add_to_nutrition_log, name="add_to_nutrition_log"),
    path("delete/<int:log_id>/", views.delete_log, name="delete_log"),
]

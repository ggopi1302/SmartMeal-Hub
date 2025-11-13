from django.urls import path
from . import views

app_name = "grocery"

urlpatterns = [
    path("generate/<int:plan_id>/", views.generate_shopping_list, name="generate_from_plan"),
    path("list/<int:pk>/", views.shopping_list_detail, name="shopping_list_detail"),
    path("toggle-item/<int:item_id>/", views.toggle_item_status, name="toggle_item_status"),
]

from django.shortcuts import render, redirect

# Create your views here.
from .models import NutritionGoal, NutritionLog
from meal.models import Meal
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages
from django.db import IntegrityError

@login_required
def nutrition_dashboard(request):
    user = request.user
    today = timezone.now().date()

    goal, _ = NutritionGoal.objects.get_or_create(user=user)

    # today's logs
    logs = NutritionLog.objects.filter(user=user, date=today)

    totals = logs.aggregate(
        total_calories=Sum('calories') or 0,
        total_protein=Sum('protein') or 0,
        total_carbs=Sum('carbs') or 0,
        total_fats=Sum('fats') or 0
    )

    context = {
        "goal": goal,
        "logs": logs,
        "totals": totals,
    }

    return render(request, "nutrition_dashboard.html", context)


@login_required
def add_to_nutrition_log(request, meal_id):
    meal = Meal.objects.get(id=meal_id)
    today = timezone.now().date()

    # Check manually before inserting
    exists = NutritionLog.objects.filter(
        user=request.user,
        meal=meal,
        date=today
    ).exists()

    if exists:
        messages.warning(request, f"{meal.name} is already added to your log today.")
        return redirect("nutrition:nutrition_dashboard")

    # Try saving — now the date is manually set
    try:
        NutritionLog.objects.create(
            user=request.user,
            meal=meal,
            date=today
        )
        messages.success(request, f"{meal.name} added to your daily nutrition log.")
    except IntegrityError:
        messages.warning(request, f"{meal.name} is already added to your log today.")

    return redirect("nutrition:nutrition_dashboard")


@login_required
def delete_log(request, log_id):
    log = NutritionLog.objects.filter(id=log_id, user=request.user).first()

    if not log:
        messages.error(request, "Log not found.")
        return redirect("nutrition:nutrition_dashboard")

    log.delete()
    messages.success(request, "Meal removed from your nutrition log.")
    return redirect("nutrition:nutrition_dashboard")


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Meal, MealPlan, MealPlanItem, MealQuiz
import random
from django.db.models import Count


@login_required
def meal_quiz(request):
    """
    Collect meal plan preferences and save them in MealQuiz model.
    """
    user = request.user

    quiz, created = MealQuiz.objects.get_or_create(user=user)

    if request.method == "POST":
        quiz.weekly_budget_limit = request.POST.get("weekly_budget_limit") or 0
        quiz.meal_frequency = request.POST.get("meal_frequency", "3_meals")
        quiz.goal = request.POST.get("goal", "general_health")
        quiz.food_preference = request.POST.get("food_preference", "omnivore") 
        quiz.max_calories = request.POST.get("max_calories") or None
        quiz.notes = request.POST.get("notes", "")
        quiz.save()

        messages.success(request, "✅ Your meal preferences have been saved successfully!")
        return redirect("meal:generate")

    context = {"quiz": quiz}
    return render(request, "meal_quiz.html", context)


@login_required
def generate_meal_plan(request):
    """
    Generate a personalized meal plan based on user quiz preferences and TheMealDB data.
    """
    user = request.user

    try:
        quiz = user.meal_quiz
    except MealQuiz.DoesNotExist:
        messages.warning(request, "Please complete your meal quiz first.")
        return redirect("meal:quiz")

    goal = quiz.goal or "general_health"
    weekly_budget = float(quiz.weekly_budget_limit or 50)
    meal_frequency = quiz.meal_frequency or "3_meals"
    max_calories = int(quiz.max_calories or 700)
    notes = quiz.notes or ""
    food_pref = quiz.food_preference or "omnivore"

    meal_count = 5 if meal_frequency == "5_meals" else 3

    # Base queryset
    meals = Meal.objects.all()

    # Apply Food Preference Filter
    if food_pref == "vegetarian":
        meals = meals.filter(category__iexact="Vegetarian")
    elif food_pref == "vegan":
        meals = meals.filter(category__iexact="Vegan")
    elif food_pref == "meat_lover":
        meals = meals.filter(category__in=["Beef", "Chicken", "Lamb", "Pork", "Goat"])
    elif food_pref == "pescatarian":
        meals = meals.filter(category__in=["Seafood", "Vegetarian"])
    elif food_pref == "light_meals":
        meals = meals.filter(category__in=["Breakfast", "Side", "Starter"])
    elif food_pref == "sweet_tooth":
        meals = meals.filter(category__in=["Dessert", "Miscellaneous"])
    elif food_pref == "high_protein":
        meals = meals.filter(category__in=["Beef", "Chicken", "Lamb", "Pork", "Seafood"])
    # 'omnivore' → no filter, includes all meals

    # Apply Goal Filters
    if goal == "weight_loss":
        meals = meals.filter(calories__lte=max_calories)
    elif goal == "muscle_gain":
        meals = meals.filter(protein__gte=10)
    elif goal == "general_health":
        meals = meals.filter(calories__lte=700)
    elif goal == "maintain_weight":
        meals = meals.filter(calories__range=(400, 800))

    if not meals.exists():
        messages.warning(request, "No meals found matching your preferences.")
        return redirect("meal:quiz")

    # Create a new plan
    plan = MealPlan.objects.create(user=user, goal=goal)
    total_budget_used = 0

    # Day and meal slots
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    meal_times = (
        ['breakfast', 'lunch', 'dinner']
        if meal_count == 3
        else ['breakfast', 'snack_1', 'lunch', 'snack_2', 'dinner']
    )

    # Generate plan
    for day in days:
        available_meals = list(meals)
        random.shuffle(available_meals)
        selected_meals = available_meals[:len(meal_times)]

        for i, meal in enumerate(selected_meals):
            MealPlanItem.objects.create(
                meal_plan=plan,
                meal=meal,
                day_of_week=day,
                meal_time=meal_times[i],
                notes=notes
            )
            total_budget_used += float(meal.price_per_serving or 0)

    # Update totals
    plan.total_budget = round(total_budget_used, 2)
    plan.update_totals()

    messages.success(request, "Your personalized weekly meal plan has been generated successfully!")
    return redirect("meal:plan")


@login_required
def view_meal_plan(request):
    user = request.user

    plan = (
        MealPlan.objects.filter(user=user)
        .annotate(item_count=Count('mealplanitem'))
        .filter(item_count__gt=0)
        .order_by('-week_start_date')
        .first()
    )

    if not plan:
        messages.info(request, "No meal plan found. Please generate one first.")
        return redirect("meal:quiz")

    items = (
        MealPlanItem.objects.filter(meal_plan=plan)
        .select_related('meal')
        .order_by('day_of_week', 'meal_time')
    )

    print(f"Showing Plan ID: {plan.id}, Items Found: {items.count()}")

    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
            'saturday', 'sunday']

    grouped_meals = {day: [] for day in days}

    for item in items:
        day_key = item.day_of_week.strip().lower()

        if day_key in grouped_meals:
            grouped_meals[day_key].append(item)
        else:
            print("⚠ INVALID DAY IN DB:", item.day_of_week)

    quiz = getattr(user, "meal_quiz", None)
    user_info = {
        "goal": quiz.goal if quiz else "-",
        "meal_frequency": quiz.meal_frequency if quiz else "-",
        "weekly_budget_limit": quiz.weekly_budget_limit if quiz else "-",
        "max_calories": quiz.max_calories if quiz else "-",
        "food_preference": quiz.food_preference if quiz else "-",
        "notes": quiz.notes if quiz else "-",
    }

    context = {
        "plan": plan,
        "items": items,
        "days": days,
        "grouped_meals": grouped_meals,
        "user_info": user_info,
    }

    return render(request, "view_meal_plan.html", context)

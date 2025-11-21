from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Leftover
from .recommendations import (
    SUBSTITUTIONS,
    find_meals_from_leftovers,
    meal_recommend_tfidf,
    rule_based_ranking
)


@login_required
def leftover_input(request):
    """Accept leftover ingredients from the user (comma-separated)."""
    if request.method == "POST":
        raw_input = request.POST.get("leftovers", "")

        # Convert "tomato, rice" → ["tomato", "rice"]
        items = [i.strip().lower() for i in raw_input.split(",") if i.strip()]

        if not items:
            messages.warning(request, "Please enter at least one leftover ingredient.")
            return redirect("leftovers:input")

        # Clear old leftovers → fresh input every time
        Leftover.objects.filter(user=request.user).delete()

        # Save new leftovers
        for item in items:
            Leftover.objects.create(user=request.user, name=item)

        messages.success(request, "Leftovers saved! Finding meals you can cook...")
        return redirect("leftovers:recommend")

    return render(request, "leftovers_input.html")


@login_required
def leftover_recommend(request):
    leftover_items = list(
        Leftover.objects.filter(user=request.user).values_list("name", flat=True)
    )

    if not leftover_items:
        messages.info(request, "Please enter leftover items first.")
        return redirect("leftovers:input")

    # Content-Based Filtering
    tfidf_meals = meal_recommend_tfidf(leftover_items)

    # Rule-Based Ranking
    ranked_meals = rule_based_ranking(tfidf_meals, leftover_items)

    # Ingredient Substitution Engine
    final_meals = []

    for meal in ranked_meals:
        ingredients = meal.ingredients.lower()

        # Direct matches + list of matched items
        direct_match_list = [item for item in leftover_items if item.lower() in ingredients]
        direct_match = len(direct_match_list)

        # Substitution matches + detailed list
        substitute_match = 0
        substitute_match_list = []

        for item in leftover_items:
            subs = SUBSTITUTIONS.get(item.lower(), [])
            for sub in subs:
                if sub.lower() in ingredients:
                    substitute_match += 1
                    substitute_match_list.append({
                        "leftover": item,
                        "used": sub
                    })

        # Attach to meal object
        meal.direct_match = direct_match
        meal.direct_match_list = direct_match_list

        meal.substitute_match = substitute_match
        meal.substitute_match_list = substitute_match_list

        # Final hybrid score
        meal.score = round(
            float(meal.final_score) + (direct_match * 0.5) + (substitute_match * 0.3),
            2
        )

        final_meals.append(meal)

    # Sort + show top 12
    final_meals = sorted(final_meals, key=lambda x: x.score, reverse=True)[:12]

    context = {
        "leftovers": leftover_items,
        "meals": final_meals,
    }

    return render(request, "leftovers_recommend.html", context)

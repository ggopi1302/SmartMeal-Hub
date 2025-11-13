from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from meal.models import MealPlan
from grocery.utils import create_shopping_list_from_mealplan, compare_outlet_prices
from grocery.models import ShoppingList, ShoppingListItem
from django.http import JsonResponse


@login_required
def generate_shopping_list(request, plan_id):
    plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
    shopping_list = create_shopping_list_from_mealplan(request.user, plan)
    return redirect("grocery:shopping_list_detail", pk=shopping_list.id)


@login_required
def shopping_list_detail(request, pk):
    shopping_list = get_object_or_404(ShoppingList, id=pk, user=request.user)
    outlet_comparisons = compare_outlet_prices(shopping_list)

    context = {
        "shopping_list": shopping_list,
        "outlet_comparisons": outlet_comparisons,
    }
    return render(request, "shopping_list_detail.html", context)

@login_required
@require_POST
def toggle_item_status(request, item_id):
    item = get_object_or_404(ShoppingListItem, id=item_id, shopping_list__user=request.user)
    item.is_purchased = not item.is_purchased
    item.save()
    return JsonResponse({"status": "ok", "purchased": item.is_purchased})

from grocery.models import GroceryItem, ShoppingList, ShoppingListItem, GroceryOutlet
from decimal import Decimal
from collections import Counter
import re


def normalize_ingredient(name):
    """Clean and normalize ingredient names."""
    # Remove quantities and parentheses
    name = re.sub(r"\(.*?\)", "", name).strip().lower()

    # Simplify plurals (e.g., onions → onion)
    if name.endswith("s") and len(name) > 3:
        name = name[:-1]

    # Basic normalization mapping
    common_map = {
        "red onion": "onion",
        "yellow onion": "onion",
        "white onion": "onion",
        "garlic clove": "garlic",
        "clove garlic": "garlic",
        "bell pepper": "pepper",
        "red pepper": "pepper",
        "green pepper": "pepper",
        "olive oil": "oil",
        "vegetable oil": "oil",
        "butter": "butter",
        "egg": "eggs",
        "tomatoes": "tomato",
        "potatoes": "potato",
        "chilies": "chili",
        "chillies": "chili",
        "milk": "milk",
        "cheese": "cheese",
    }
    for key, val in common_map.items():
        if key in name:
            name = val
            break

    return name.strip()


def create_shopping_list_from_mealplan(user, mealplan):
    """Generate a simplified and realistic shopping list from the meal plan."""
    ingredients = []

    # Collect all meal ingredients
    for item in mealplan.mealplanitem_set.select_related("meal"):
        ing_str = item.meal.ingredients or ""
        for i in ing_str.split(","):
            name = normalize_ingredient(i)
            if name:
                ingredients.append(name)

    counts = Counter(ingredients)

    # Ignore generic, trivial ingredients
    ignore_list = {
        "salt", "water", "oil", "pepper", "sugar",
        "flour", "seasoning", "spices", "stock", "broth",
        "butter", "vinegar"
    }

    filtered_counts = {
        name: qty for name, qty in counts.items()
        if name not in ignore_list and len(name) > 2
    }

    # Reduce to top 25 by frequency for simplicity
    top_items = dict(Counter(filtered_counts).most_common(25))

    # Create shopping list
    shopping_list = ShoppingList.objects.create(
        user=user, title=f"Shopping List for {mealplan.week_start_date}"
    )

    total = Decimal("0.00")

    for name, qty in top_items.items():
        grocery_item = GroceryItem.objects.filter(name__icontains=name).first()

        if not grocery_item:
            # Create placeholder if not found
            grocery_item = GroceryItem.objects.create(name=name, base_price=1.50)

        cost = Decimal(grocery_item.base_price) * qty
        ShoppingListItem.objects.create(
            shopping_list=shopping_list,
            item=grocery_item,
            quantity=qty,
            cost=cost,
        )
        total += cost

    shopping_list.total_cost = total
    shopping_list.save()
    return shopping_list


def compare_outlet_prices(shopping_list):
    """Compare total grocery cost across outlets."""
    outlets = GroceryOutlet.objects.all()
    results = []

    for outlet in outlets:
        outlet_total = Decimal("0.00")
        for item in shopping_list.items.all():
            outlet_total += Decimal(item.item.base_price) * Decimal(outlet.price_factor) * item.quantity
        results.append({
            "outlet": outlet.name,
            "total": round(outlet_total, 2)
        })

    return results

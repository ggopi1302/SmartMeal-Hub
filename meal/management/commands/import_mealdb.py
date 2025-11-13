import requests
import random
from django.core.management.base import BaseCommand
from meal.models import Meal

CATEGORIES = [
    "Beef", "Chicken", "Dessert", "Lamb", "Miscellaneous",
    "Pasta", "Pork", "Seafood", "Side", "Starter",
    "Vegan", "Vegetarian", "Breakfast", "Goat"
]

API_BASE = "https://www.themealdb.com/api/json/v1/1"

class Command(BaseCommand):
    help = "Import meals from TheMealDB API into the Meal model"

    def handle(self, *args, **options):
        total_imported = 0

        for category in CATEGORIES:
            self.stdout.write(self.style.WARNING(f"\n Fetching meals from category: {category}"))
            list_url = f"{API_BASE}/filter.php?c={category}"
            response = requests.get(list_url)
            data = response.json()

            if not data.get("meals"):
                self.stdout.write(self.style.ERROR(f" No meals found for {category}."))
                continue

            for meal_summary in data["meals"]:
                meal_id = meal_summary["idMeal"]

                # Skip duplicates
                if Meal.objects.filter(name__iexact=meal_summary["strMeal"]).exists():
                    continue

                # Get full meal details
                meal_url = f"{API_BASE}/lookup.php?i={meal_id}"
                meal_data = requests.get(meal_url).json().get("meals", [])[0]

                ingredients = []
                for i in range(1, 21):
                    ingredient = meal_data.get(f"strIngredient{i}")
                    measure = meal_data.get(f"strMeasure{i}")
                    if ingredient:
                        ingredients.append(f"{ingredient} ({measure.strip()})" if measure else ingredient)

                Meal.objects.create(
                    name=meal_data.get("strMeal", "Unknown Meal"),
                    category=meal_data.get("strCategory", ""),
                    area=meal_data.get("strArea", ""),
                    tags=meal_data.get("strTags", "") or "",
                    description=meal_data.get("strMeal", ""),
                    ingredients=", ".join(ingredients),
                    instructions=meal_data.get("strInstructions", ""),
                    cooking_time=random.randint(15, 30),
                    calories=random.randint(250, 700),
                    price_per_serving=round(random.uniform(2.5, 8.0), 2),
                    image_url=meal_data.get("strMealThumb", ""),
                )

                total_imported += 1

            self.stdout.write(self.style.SUCCESS(f" Imported meals from category: {category}"))

        self.stdout.write(self.style.SUCCESS(f"\n Done! Imported {total_imported} meals successfully!"))

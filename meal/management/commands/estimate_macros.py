from django.core.management.base import BaseCommand
from meal.models import Meal

class Command(BaseCommand):
    help = "Estimate macros for meals based on calories"

    def handle(self, *args, **options):
        for meal in Meal.objects.all():
            if not meal.calories:
                continue

            calories = meal.calories

            # Choose ratio (example: general health)
            protein_ratio = 0.25
            carb_ratio = 0.50
            fat_ratio = 0.25

            # Convert kcal → grams
            protein = (calories * protein_ratio) / 4
            carbs = (calories * carb_ratio) / 4
            fats = (calories * fat_ratio) / 9

            # Round & save
            meal.protein = round(protein, 1)
            meal.carbs = round(carbs, 1)
            meal.fats = round(fats, 1)
            meal.save()

            self.stdout.write(f"✅ Updated {meal.name}: {meal.protein}g P, {meal.carbs}g C, {meal.fats}g F")

        self.stdout.write(self.style.SUCCESS("🎉 Macro estimation completed!"))

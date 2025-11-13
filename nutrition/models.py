from django.conf import settings
from django.db import models
from django.utils import timezone 

class NutritionGoal(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    daily_calorie_goal = models.PositiveIntegerField(default=2000)
    daily_protein_goal = models.FloatField(default=100.0)
    daily_carbs_goal = models.FloatField(default=250.0)
    daily_fats_goal = models.FloatField(default=70.0)

    def __str__(self):
        return f"{self.user.username}'s Nutrition Goals"


class NutritionLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    meal = models.ForeignKey('meal.Meal', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)

    calories = models.PositiveIntegerField(default=0)
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fats = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        if self.meal:
            self.calories = self.meal.calories
            self.protein = self.meal.protein
            self.carbs = self.meal.carbs
            self.fats = self.meal.fats
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.meal.name} ({self.date})"

    class Meta:
        unique_together = ('user', 'meal', 'date')

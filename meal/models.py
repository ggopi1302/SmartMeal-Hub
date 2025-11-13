from django.db import models
from django.conf import settings
from django.utils import timezone


class Meal(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True, help_text="e.g., Beef, Chicken, Vegan")
    area = models.CharField(max_length=100, blank=True, help_text="Country or region of origin")
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags from API")

    description = models.TextField(blank=True)
    ingredients = models.TextField(help_text="List of ingredients, comma-separated", blank=True)
    instructions = models.TextField(blank=True)
    cooking_time = models.PositiveIntegerField(
        help_text="Approximate cooking time in minutes", default=30
    )

    # Nutrition info (optional)
    calories = models.PositiveIntegerField(default=300, help_text="Estimated calories per serving")
    protein = models.FloatField(null=True, blank=True, help_text="grams")
    carbs = models.FloatField(null=True, blank=True, help_text="grams")
    fats = models.FloatField(null=True, blank=True, help_text="grams")

    # Cost and image
    price_per_serving = models.DecimalField(
        max_digits=6, decimal_places=2,
        help_text="Approx. cost per serving in $", null=True, blank=True
    )
    image_url = models.URLField(blank=True, null=True, help_text="External image URL")

    # Ratings / metadata
    average_rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class MealQuiz(models.Model):
    """Stores user preferences for generating personalized meal plans."""

    MEAL_FREQUENCY_CHOICES = [
        ('3_meals', '3 Meals a Day'),
        ('5_meals', '5 Small Meals a Day'),
    ]

    GOAL_CHOICES = [
        ('general_health', 'General Health'),
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintain_weight', 'Maintain Weight'),
    ]

    FOOD_PREFERENCES = [
        ('omnivore', 'Omnivore (All Foods)'),
        ('meat_lover', 'Meat Lover'),
        ('pescatarian', 'Pescatarian'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('high_protein', 'High Protein / Gym Diet'),
        ('light_meals', 'Breakfast & Light Meals'),
        ('sweet_tooth', 'Sweet Tooth / Dessert Lover'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meal_quiz'
    )

    weekly_budget_limit = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Maximum budget per week in USD"
    )
    meal_frequency = models.CharField(
        max_length=20, choices=MEAL_FREQUENCY_CHOICES, default='3_meals'
    )
    goal = models.CharField(
        max_length=50, choices=GOAL_CHOICES, default='general_health'
    )

    # New field: Food preference
    food_preference = models.CharField(
        max_length=30, choices=FOOD_PREFERENCES, default='omnivore',
        help_text="Preferred type of meals (e.g., Vegetarian, Vegan, etc.)"
    )

    max_calories = models.PositiveIntegerField(
        null=True, blank=True, help_text="Max calories per meal"
    )
    notes = models.TextField(blank=True, help_text="Allergies or special notes")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Meal Preferences"


class MealPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="My Weekly Plan")
    week_start_date = models.DateField(default=timezone.now)
    week_end_date = models.DateField(blank=True, null=True)
    meals = models.ManyToManyField(Meal, through='MealPlanItem')

    total_calories = models.PositiveIntegerField(default=0)
    total_budget = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    goal = models.CharField(max_length=100, blank=True, help_text="e.g., Weight Loss, Muscle Gain")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s plan ({self.week_start_date})"

    def update_totals(self):
        items = self.mealplanitem_set.select_related('meal')
        self.total_calories = sum(item.meal.calories for item in items)
        self.total_budget = sum(item.meal.price_per_serving or 0 for item in items)
        self.save()

    class Meta:
        ordering = ['-week_start_date']


class MealPlanItem(models.Model):
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    day_of_week = models.CharField(
        max_length=10,
        choices=[
            ('monday', 'Monday'),
            ('tuesday', 'Tuesday'),
            ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'),
            ('friday', 'Friday'),
            ('saturday', 'Saturday'),
            ('sunday', 'Sunday'),
        ],
    )
    meal_time = models.CharField(
        max_length=20,
        choices=[
            ('breakfast', 'Breakfast'),
            ('lunch', 'Lunch'),
            ('dinner', 'Dinner'),
            ('snack', 'Snack'),
        ],
    )
    portion_size = models.PositiveIntegerField(default=1, help_text="Number of servings")
    notes = models.TextField(blank=True, help_text="Custom notes or modifications")

    class Meta:
        ordering = ['day_of_week', 'meal_time']

    def __str__(self):
        return f"{self.meal_plan.user.username} - {self.day_of_week} {self.meal_time}: {self.meal.name}"

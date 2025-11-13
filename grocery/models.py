from django.db import models
from django.conf import settings
from decimal import Decimal


class GroceryOutlet(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price_factor = models.FloatField(default=1.0, help_text="Multiplier for relative pricing differences")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GroceryItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.name} (${self.base_price})"


class ShoppingList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Weekly Shopping List")
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ShoppingListItem(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey(GroceryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    is_purchased = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.item.name} x{self.quantity}"

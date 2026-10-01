from django.contrib.auth.models import AbstractUser
from django.db import models

# Models for the e-commerce app
# task completed

class User(AbstractUser):
    full_name = models.CharField(max_length=150)

    phone_number = models.CharField(
        max_length=20,
        unique=True
    )

    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username





class Category(models.Model):#this class is to push in db and id . id auto generate huncha 
    name =models.CharField(max_length=100)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name




    # '''''''''''''''''''''''''''''''''''''''''''''
class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartDetails(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="cart_details"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    price_per = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.IntegerField()

    @property
    def total_amount(self):
        return self.price_per * self.quantity

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
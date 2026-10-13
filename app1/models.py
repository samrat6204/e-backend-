from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg, Count

# Models for the e-commerce app
# updated: Week 7 - Ratings & Reviews


class User(AbstractUser):
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    # NEW: cached rating stats, so product pages don't recalculate every view
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    # NEW: recalculates stats from approved ratings only
    def update_rating_stats(self):
        stats = self.ratings.filter(status="approved").aggregate(
            avg=Avg("score"), count=Count("id")
        )
        self.average_rating = round(stats["avg"] or 0, 1)
        self.review_count = stats["count"]
        self.save(update_fields=["average_rating", "review_count"])


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartDetails(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="cart_details"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price_per = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    @property
    def total_amount(self):
        return self.price_per * self.quantity

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


# ============================================================
# RATING & REVIEW
# ============================================================

class Rating(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        HIDDEN = "hidden", "Hidden"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings")

    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, max_length=1000)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.APPROVED
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_rating_per_user_product"
            ),
            # On Django older than 5.1, change `condition=` to `check=`
            models.CheckConstraint(
                condition=models.Q(score__gte=1, score__lte=5),
                name="rating_score_between_1_and_5",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} rated {self.product.name}: {self.score}"
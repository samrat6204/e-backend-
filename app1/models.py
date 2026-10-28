from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg, Count
from django.utils import timezone

# Models for the e-commerce app
# updated: Week 7 - Ratings & Reviews, Coupons
# updated: Payment & checkout revision - Order, OrderItem (added at the bottom)


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

    # cached rating stats, so product pages don't recalculate every view
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    # recalculates stats from approved ratings only
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
            models.CheckConstraint(
                condition=models.Q(score__gte=1, score__lte=5),
                name="rating_score_between_1_and_5",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} rated {self.product.name}: {self.score}"


# ============================================================
# COUPON
# ============================================================

class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage"
        FIXED = "fixed", "Fixed amount"

    code = models.CharField(max_length=30, unique=True)
    discount_type = models.CharField(max_length=12, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)

    # for percentage coupons: the most money one coupon can take off (optional)
    max_discount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    min_order_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    start_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField()

    # empty = unlimited uses
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.discount_value is not None and self.discount_value <= 0:
            raise ValidationError("Discount value must be more than 0.")
        if (
            self.discount_type == self.DiscountType.PERCENTAGE
            and self.discount_value is not None
            and self.discount_value > 100
        ):
            raise ValidationError("Percentage cannot be more than 100.")
        if self.expiry_date and self.start_date and self.expiry_date <= self.start_date:
            raise ValidationError("Expiry date must be after the start date.")

    def save(self, *args, **kwargs):
        # always store the code in capital letters, so "save10" = "SAVE10"
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code


# ============================================================
# ORDER  (NEW - payment & checkout revision)
# ============================================================

class Order(models.Model):
    class PaymentMethod(models.TextChoices):
        COD = "cod", "Cash on Delivery"
        ONLINE = "online", "Online Payment (QR)"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    class OrderStatus(models.TextChoices):
        PLACED = "placed", "Placed"
        CONFIRMED = "confirmed", "Confirmed"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")

    # delivery details (saved on the order, so later profile changes don't alter it)
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=500)
    note = models.CharField(max_length=500, blank=True)

    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices)
    payment_status = models.CharField(
        max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    # optional: transaction id the customer types after paying by QR
    payment_reference = models.CharField(max_length=100, blank=True)
    terms_accepted = models.BooleanField(default=False)

    order_status = models.CharField(
        max_length=10, choices=OrderStatus.choices, default=OrderStatus.PLACED
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def order_number(self):
        return f"ORD-{self.pk:06d}"

    def __str__(self):
        return f"{self.order_number} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    # product can be deleted later, the order history must stay
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=100)
    price_per = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    @property
    def total_amount(self):
        return self.price_per * self.quantity

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
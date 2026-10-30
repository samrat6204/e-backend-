from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.html import strip_tags

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    User,
    Category,
    Product,
    Cart,
    CartDetails,
    Rating,
    Coupon,
    Order,
    OrderItem,
)


# ============================================================
# REGISTER SERIALIZER
# ============================================================

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "full_name",
            "phone_number",
            "email",
            "password",
        ]

    def create(self, validated_data):

        user = User.objects.create_user(
            username=validated_data["username"],
            full_name=validated_data["full_name"],
            phone_number=validated_data["phone_number"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        return user


# ============================================================
# LOGIN SERIALIZER
# ============================================================

class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, data):

        user = authenticate(
            username=data["username"],
            password=data["password"]
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive."
            )

        refresh = RefreshToken.for_user(user)

        return {
            "message": "Login successful.",

            "user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "phone_number": user.phone_number,
                # True for admin (staff) accounts, False for customers
                "is_admin": user.is_staff,
            },

            "tokens": {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            }
        }


# ============================================================
# CATEGORY SERIALIZER
# ============================================================

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields = [
            "id",
            "name",
            "description",
        ]


# ============================================================
# PRODUCT SERIALIZER
# ============================================================

class ProductSerializer(serializers.ModelSerializer):

    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    # kept so your React code that uses "rating_count" keeps working
    rating_count = serializers.IntegerField(
        source="review_count",
        read_only=True
    )

    # False when the stock is finished
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Product

        fields = [
            "id",
            "name",
            "description",
            "price",
            "quantity",
            "is_available",
            "category",
            "average_rating",
            "review_count",
            "rating_count",
        ]

    def get_is_available(self, obj):
        return obj.quantity > 0

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be more than 0.")
        return value


# ============================================================
# CART DETAILS SERIALIZER
# ============================================================

class CartDetailsSerializer(serializers.ModelSerializer):

    total_amount = serializers.ReadOnlyField()
    product_name = serializers.SerializerMethodField()
    available_quantity = serializers.SerializerMethodField()

    class Meta:
        model = CartDetails

        fields = [
            "id",
            "cart",
            "product",
            "product_name",
            "price_per",
            "quantity",
            "total_amount",
            "available_quantity",
        ]

    def get_product_name(self, obj):
        return obj.product.name

    def get_available_quantity(self, obj):
        return obj.product.quantity


# ============================================================
# CART SERIALIZER
# ============================================================

class CartSerializer(serializers.ModelSerializer):

    cart_details = CartDetailsSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Cart

        fields = [
            "id",
            "user",
            "cart_details",
        ]


# ============================================================
# RATING / REVIEW SERIALIZER
# ============================================================

class RatingSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    class Meta:
        model = Rating

        fields = [
            "id",
            "product",
            "username",
            "score",
            "comment",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "product",
            "username",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate_comment(self, value):
        # remove any HTML tags and extra spaces
        return strip_tags(value).strip()


# ============================================================
# MODERATION SERIALIZER (admin only)
# ============================================================

class RatingModerationSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    class Meta:
        model = Rating

        fields = [
            "id",
            "product",
            "product_name",
            "username",
            "score",
            "comment",
            "status",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "product",
            "product_name",
            "username",
            "score",
            "comment",
            "created_at",
        ]


# ============================================================
# COUPON SERIALIZER (admin only)
# used_count is read-only: only the system changes it, never the admin
# ============================================================

class CouponSerializer(serializers.ModelSerializer):

    class Meta:
        model = Coupon

        fields = [
            "id",
            "code",
            "discount_type",
            "discount_value",
            "max_discount",
            "min_order_value",
            "start_date",
            "expiry_date",
            "usage_limit",
            "used_count",
            "is_active",
            "created_at",
        ]

        read_only_fields = ["id", "used_count", "created_at"]

    def validate_code(self, value):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError("Code cannot be empty.")

        # "save10" and "SAVE10" must count as the same code
        duplicate = Coupon.objects.filter(code__iexact=value)
        if self.instance:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise serializers.ValidationError("A coupon with this code already exists.")

        return value

    def validate_discount_value(self, value):
        if value <= 0:
            raise serializers.ValidationError("Discount value must be more than 0.")
        return value

    def validate_max_discount(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Max discount must be more than 0.")
        return value

    def validate_min_order_value(self, value):
        if value < 0:
            raise serializers.ValidationError("Minimum order value cannot be negative.")
        return value

    def validate_usage_limit(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError("Usage limit must be at least 1.")
        return value

    def validate(self, data):
        # For PATCH, fields that were not sent come from the saved coupon.
        def current(field):
            if field in data:
                return data[field]
            return getattr(self.instance, field, None)

        discount_type = current("discount_type")
        discount_value = current("discount_value")
        start_date = current("start_date") or timezone.now()
        expiry_date = current("expiry_date")

        if (
            discount_type == Coupon.DiscountType.PERCENTAGE
            and discount_value is not None
            and discount_value > 100
        ):
            raise serializers.ValidationError(
                {"discount_value": "Percentage cannot be more than 100."}
            )

        if expiry_date and expiry_date <= start_date:
            raise serializers.ValidationError(
                {"expiry_date": "Expiry date must be after the start date."}
            )

        # a usage limit lower than the times already used makes no sense
        new_limit = current("usage_limit")
        if self.instance and new_limit is not None and new_limit < self.instance.used_count:
            raise serializers.ValidationError(
                {"usage_limit": "Usage limit cannot be lower than the times already used."}
            )

        return data


# ============================================================
# ORDER SERIALIZERS  (NEW - payment & checkout revision)
# ============================================================

class OrderItemSerializer(serializers.ModelSerializer):

    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem

        fields = [
            "id",
            "product",
            "product_name",
            "price_per",
            "quantity",
            "total_amount",
        ]


class OrderSerializer(serializers.ModelSerializer):

    order_number = serializers.ReadOnlyField()
    items = OrderItemSerializer(many=True, read_only=True)
    payment_method_label = serializers.CharField(
        source="get_payment_method_display",
        read_only=True
    )

    class Meta:
        model = Order

        fields = [
            "id",
            "order_number",
            "full_name",
            "phone_number",
            "address",
            "note",
            "payment_method",
            "payment_method_label",
            "payment_status",
            "payment_reference",
            "terms_accepted",
            "order_status",
            "subtotal",
            "delivery_fee",
            "total",
            "items",
            "created_at",
        ]


# What React sends when the customer presses "Place Order".
# Items are NOT sent: the server reads them from the user's own cart,
# so nobody can fake prices or quantities.
class PlaceOrderSerializer(serializers.Serializer):

    full_name = serializers.CharField(max_length=150)
    phone_number = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=500)
    note = serializers.CharField(max_length=500, required=False, allow_blank=True, default="")

    payment_method = serializers.ChoiceField(choices=Order.PaymentMethod.choices)

    # must be true for Cash on Delivery
    terms_accepted = serializers.BooleanField(required=False, default=False)

    # optional: transaction id after paying by QR
    payment_reference = serializers.CharField(
        max_length=100, required=False, allow_blank=True, default=""
    )

    # optional: which cart lines to order (CartDetails ids).
    # If it is missing, the whole cart is ordered.
    item_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=False,
    )

    def validate_full_name(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Full name is required.")
        return value

    def validate_phone_number(self, value):
        value = strip_tags(value).strip()
        digits = value.replace("+", "").replace("-", "").replace(" ", "")
        if not digits.isdigit() or len(digits) < 7:
            raise serializers.ValidationError("Enter a valid phone number.")
        return value

    def validate_address(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Delivery address is required.")
        return value

    def validate_note(self, value):
        return strip_tags(value).strip()

    def validate_payment_reference(self, value):
        return strip_tags(value).strip()

    def validate(self, data):
        if (
            data["payment_method"] == Order.PaymentMethod.COD
            and not data.get("terms_accepted")
        ):
            raise serializers.ValidationError(
                {"terms_accepted": "You must accept the terms and conditions for Cash on Delivery."}
            )
        return data
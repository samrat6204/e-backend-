from django.contrib.auth import authenticate
from django.utils.html import strip_tags

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Category, Product, Cart, CartDetails, Rating


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
# average_rating and review_count are now stored on the Product,
# so no extra database work is needed for each product.
# ============================================================

class ProductSerializer(serializers.ModelSerializer):

    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    # kept so your React code that uses "rating_count" keeps working
    rating_count = serializers.IntegerField(
        source="review_count",
        read_only=True
    )

    class Meta:
        model = Product

        fields = [
            "id",
            "name",
            "description",
            "price",
            "quantity",
            "category",
            "average_rating",
            "review_count",
            "rating_count",
        ]


# ============================================================
# CART DETAILS SERIALIZER
# ============================================================

class CartDetailsSerializer(serializers.ModelSerializer):

    total_amount = serializers.ReadOnlyField()
    product_name = serializers.SerializerMethodField()

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
        ]

    def get_product_name(self, obj):
        return obj.product.name


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
# The user can only send "score" and "comment".
# product, user and status are set by the server, never by the client.
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
# Admin can change only the status.
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
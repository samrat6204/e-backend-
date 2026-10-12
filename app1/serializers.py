from django.contrib.auth import authenticate
from django.db.models import Avg

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
# OLD PROFILE SERIALIZER
# ============================================================

# class ProfileSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User

#         fields = [
#             "id",
#             "username",
#             "full_name",
#             "email",
#             "phone_number",
#         ]


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
# PRODUCT SERIALIZER  (rating fields added)
# ============================================================

class ProductSerializer(serializers.ModelSerializer):

    average_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()

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
            "rating_count",
        ]

    def get_average_rating(self, obj):
        avg = obj.ratings.aggregate(avg=Avg("score"))["avg"]
        return round(avg, 1) if avg else 0

    def get_rating_count(self, obj):
        return obj.ratings.count()


# ============================================================
# OLD PRODUCT LIST SERIALIZER
# ============================================================

# class ProductListSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Product

#         fields = [
#             "id",
#             "name",
#             "price",
#         ]


# ============================================================
# OLD PRODUCT DETAIL SERIALIZER
# ============================================================

# class ProductDetailSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Product

#         fields = [
#             "id",
#             "name",
#             "description",
#             "price",
#             "quantity",
#             "category",
#         ]


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
# RATING SERIALIZER (NEW)
# ============================================================

class RatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        fields = ["id", "product", "score"]
from django.contrib.auth import authenticate


from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User,Category,Product


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





class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

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




class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields = [
            "id",
            "name",
            "description",
        ]


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product

        fields = [
            "id",
            "name",
            "description",
            "price",
            "quantity",
            "category",
        ]


# class ProductListSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Product

#         fields = [
#             "id",
#             "name",
#             "price",
#         ]




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
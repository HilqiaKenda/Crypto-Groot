from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Payment, SubscriptionPlan, User, UserUsageLog, Watchlist


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class RegisterUserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {"password": {"write_only":True}}


class LoginSerializer(Serializer):
    username = serializers.CharField(max_length=100)
    # email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)

        if user and user.is_active:
            return user
        
        raise serializers.ValidationError("Incorect credential!")
    

class WatchlistSerializer(ModelSerializer):
    model = Watchlist
    fields = ["id", "user", "symbol"]



class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "plan", "timestamp"]
        # read_only_fields = ["transaction_id", "user", "amount", ""]

    def validate(self, data):
        plan = data.get("plan")

        if plan and not data.get("amount"):
            data["amount"] = plan.price

        return data


class UserUsageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserUsageLog
        fields = "__all__"


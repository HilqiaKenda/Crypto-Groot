from rest_framework import viewsets, routers, serializers
from .models import User, SubscriptionPlan, Payment, UserUsageLog, Watchlist


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

    def validate(self, data):
        plan = data.get("plan")

        if plan and not data.get("amount"):
            data["amount"] = plan.price

        return data


class UserUsageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserUsageLog
        fields = "__all__"


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = "__all__"


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class UserUsageLogViewSet(viewsets.ModelViewSet):
    queryset = UserUsageLog.objects.all()
    serializer_class = UserUsageLogSerializer


class WatchlistViewSet(viewsets.ModelViewSet):
    queryset = Watchlist.objects.all()
    serializer_class = WatchlistSerializer


router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"plans", SubscriptionPlanViewSet)
router.register(r"payments", PaymentViewSet)
router.register(r"usage-logs", UserUsageLogViewSet)
router.register(r"watchlist", WatchlistViewSet)

from django.contrib import admin
from .models import User, SubscriptionPlan, Payment, UserUsageLog, Watchlist

admin.site.register(User)
admin.site.register(SubscriptionPlan)
admin.site.register(Payment)
admin.site.register(UserUsageLog)
admin.site.register(Watchlist)

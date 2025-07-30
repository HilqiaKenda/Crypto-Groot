from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SubscriptionPlan, Payment, UserUsageLog, Watchlist






@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # model = User
    list_display = ('username', 'email', 'subscription', 'subscription_start_date', 'subscription_end_date', 'usage_count')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('subscription', 'subscription_start_date', 'subscription_end_date', 'usage_count', 'bio', 'profile_picture')}),
    )
    

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'amount', 'status', 'timestamp')
    readonly_fields = ("amount", "transaction_id")


admin.site.register(SubscriptionPlan)
admin.site.register(UserUsageLog)
admin.site.register(Watchlist)

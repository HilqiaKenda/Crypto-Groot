from django.contrib import admin
from .models import User, SubscriptionPlan, Payment, UserUsageLog, Watchlist




from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'subscription', 'subscription_start_date', 'subscription_end_date', 'usage_count')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('subscription', 'subscription_start_date', 'subscription_end_date', 'usage_count', 'bio', 'profile_picture')}),
    )
    

admin.site.register(User, CustomUserAdmin)

# admin.site.register(User)
admin.site.register(SubscriptionPlan)
admin.site.register(Payment)
admin.site.register(UserUsageLog)
admin.site.register(Watchlist)

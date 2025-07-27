from django.apps import AppConfig

class CryptoAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crypto_app'
    def ready(self):
        import crypto_app.dash_apps.main_indicators

from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        
        if not username:
            raise ValueError("Username is require")
        username = self.normalize_email(username)
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()

        return user
    
    
    def creste_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have a staff permission")
        
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have a superuser permission")
        return self.create_user(username, password, **extra_fields)
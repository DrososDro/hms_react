import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.constraints import ValidationError
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """User Manager for the custom User model"""

    def create_user(self, email, password=None):
        """Create and save User with the email and password"""
        if not email:
            raise ValueError("User must have an email address")

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """Create and saves the super user with email and password"""
        user = self.create_user(email=email)
        user.set_password(password)
        user.is_superadmin = True
        user.is_active = True
        user.is_admin = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser):
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )

    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    objects = UserManager()

    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    permissions = models.ManyToManyField("Permissions")

    USERNAME_FIELD = "email"

    def __str__(self) -> str:
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    @property
    def is_staff(self) -> bool:
        return self.is_admin

    @property
    def user_perms(self) -> list:
        """Custom user permissions"""
        return {i.name for i in self.permissions.all()}


class Permissions(models.Model):
    """Model who habe all permissions assigned to user."""

    class AdminChoices(models.TextChoices):
        """Choices class for permission"""

        ADMIN = "admin", _("Admin")
        GARAZE_ADMIN = "garaze_admin", _("Garaze_admin")
        TECHNICIAN = "technician", _("Technicial")
        B2B = "b2b", _("b2b")
        CUSTOMER = "customer", _("Customer")

    id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False
    )

    name = models.CharField(unique=True, choices=AdminChoices.choices)

    def __str__(self) -> str:
        return self.name

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)

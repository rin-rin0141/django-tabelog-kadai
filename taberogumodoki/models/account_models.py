from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from taberogumodoki.models import create_id
from django.conf import settings
from taberogumodoki.models.item_models import Item
from django.contrib.auth.models import PermissionsMixin


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(default=create_id, primary_key=True, max_length=22)
    username = models.CharField(max_length=50, unique=True, blank=True, default="匿名")
    email = models.EmailField(max_length=255, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    name = models.CharField(default="", blank=True, max_length=50)
    zipcode = models.CharField(default="", blank=True, max_length=8)
    prefecture = models.CharField(default="", blank=True, max_length=50)
    city = models.CharField(default="", blank=True, max_length=50)
    address1 = models.CharField(default="", blank=True, max_length=50)
    address2 = models.CharField(default="", blank=True, max_length=50)
    tel = models.CharField(default="", blank=True, max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=User)
def create_onetoone(sender, **kwargs):
    if kwargs["created"]:
        Profile.objects.create(user=kwargs["instance"])


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50)  # active, canceled, past_due
    current_period_end = models.DateTimeField(null=True)

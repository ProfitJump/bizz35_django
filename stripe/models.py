from django.db import models
from authentication.models import User

# Create your models here.
class Stripe(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_id = models.CharField(max_length=255, blank=True, null=True)
    connect_id = models.CharField(max_length=255, blank=True, null=True)
    disabled = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.username} Stripe Profile'
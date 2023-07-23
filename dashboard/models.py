from django.contrib.auth import get_user_model
from django.db import models
from django.db import transaction

from authentication.models import User
from stripe.models import Stripe
from mainapp.storage_backends import PublicMediaStorage, PrivateMediaStorage

import json


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    image = models.FileField(storage=PublicMediaStorage())
    company = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    referral_id = models.CharField(max_length=8, unique=True)
    referred_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='referred_by')
    membership_level = models.CharField(max_length=255)
    matrix_level = models.IntegerField(blank=True, null=True, default=0)
    ancestors = models.TextField(default='[]')
    business_centers = models.IntegerField(blank=True, null=True, default=0)
    sponsor_business_center = models.IntegerField(blank=True, null=True, default=0)
    commission_owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='commissions')

    is_booster = models.BooleanField(default=False)
    boosters = models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return f'{self.user.username} Profile'

    def get_recommended_profiles(self):
        query_set = Profile.objects.all()
        user_recommendations = [profile for profile in query_set if profile.referred_by == self.user]
        return user_recommendations

    def get_recommended_count(self):
        query_set = Profile.objects.filter(referred_by=self.user).count()

        return query_set

    def get_recommended_paid_count(self):
        query_set = Profile.objects.filter(referred_by=self.user).exclude(membership_level='Free User').count()

        return query_set

    def get_ancestors(self):
        return json.loads(self.ancestors)

    def set_ancestors(self, value):
        self.ancestors = json.dumps(value)

    ancestors_property = property(get_ancestors, set_ancestors)

    def save(self, *args, **kwargs):
        if self.referral_id == "":
            pass
        if self.referred_by:
            self.ancestors_property = self.referred_by.profile.ancestors_property + [self.referred_by.id]

        super(Profile, self).save(*args, **kwargs)

        user_tree = self.ancestors_property
        with transaction.atomic():
            try:
                business_center = Profile.objects.filter(referred_by=self.referred_by.id).count()
                if business_center == 1:
                    if not self.sponsor_business_center and business_center == 1:
                        self.referred_by.profile.business_centers += 1
                        self.sponsor_business_center = 1
                        self.referred_by.profile.save()
                        self.save()
                        print('Sponsors Business Center #: 1')

                elif business_center == 2:
                    if not self.sponsor_business_center and business_center == 2:
                        self.referred_by.profile.business_centers += 1
                        self.sponsor_business_center = 2
                        self.referred_by.profile.save()
                        self.save()
                        print('Sponsors Business Center #: 2')

                elif business_center >= 3:
                    if not self.sponsor_business_center and business_center >= 2:
                        self.referred_by.profile.business_centers += 1
                        self.referred_by.profile.save()
                        self.sponsor_business_center = self.referred_by.profile.business_centers
                        self.save()
                        print('Sponsors Business Center #:', business_center)

            except:
                pass

        try:
            if self.referred_by.profile.sponsor_business_center == 0 and self.sponsor_business_center >= 1:
                commission_owner = user_tree[0]
                User = get_user_model()
                user = User.objects.get(id=commission_owner)

                if self.commission_owner is None:
                    owner = self.commission_owner = user
                    self.commission_owner = user
                    self.save()

                    print('Commission Owner:', owner)

            elif (

                    self.referred_by.profile.sponsor_business_center == 1 and self.sponsor_business_center == 1 or
                    self.referred_by.profile.sponsor_business_center == 1 and self.sponsor_business_center == 2 or
                    self.referred_by.profile.sponsor_business_center == 2 and self.sponsor_business_center == 1 or
                    self.referred_by.profile.sponsor_business_center == 2 and self.sponsor_business_center == 2

            ):
                commission_owner = user_tree[0]
                User = get_user_model()
                user = User.objects.get(id=commission_owner)

                if self.commission_owner is None:
                    owner = self.commission_owner = user
                    self.commission_owner = user
                    self.save()

                    print('Commission Owner:', owner)

            elif (

                    self.referred_by.profile.sponsor_business_center >= 1 and self.sponsor_business_center >= 3

            ):

                generation_count = len(user_tree)
                commission_owner = generation_count - 1  # index count starts at 0, so this accounts and pulls the last ID.

                User = get_user_model()
                user = User.objects.get(id=user_tree[commission_owner])

                if self.commission_owner is None:
                    owner = self.commission_owner = user
                    self.commission_owner = user
                    self.save()

                    print('Commission Owner:', owner)

            elif (

                    self.referred_by.profile.sponsor_business_center >= 3 and self.sponsor_business_center <= 2

            ):

                generation_count = len(user_tree)
                commission_owner = generation_count - 2  # index count starts at 0, so this accounts and pulls the last but one ID.

                User = get_user_model()
                user = User.objects.get(id=user_tree[commission_owner])

                if self.commission_owner is None:
                    owner = self.commission_owner = user
                    self.commission_owner = user
                    self.save()

                    print('Commission Owner:', owner)

        except:
            pass


class LedgerEntry(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)
    debit = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    credit = models.DecimalField(max_digits=10, decimal_places=2, null=True, )

    user_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    blue_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    boosters_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    master_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    ledger_name = models.CharField(max_length=255)
    is_public = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Ledger Record'


class BoosterNumbers(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    count = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class BoosterProfile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)

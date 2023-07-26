# Generated by Django 4.2.3 on 2023-07-24 00:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mainapp.storage_backends


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(storage=mainapp.storage_backends.PublicMediaStorage(), upload_to='')),
                ('company', models.CharField(blank=True, max_length=255, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('referral_id', models.CharField(max_length=8, unique=True)),
                ('membership_level', models.CharField(max_length=255)),
                ('matrix_level', models.IntegerField(blank=True, default=0, null=True)),
                ('ancestors', models.TextField(default='[]')),
                ('business_centers', models.IntegerField(blank=True, default=0, null=True)),
                ('sponsor_business_center', models.IntegerField(blank=True, default=0, null=True)),
                ('is_booster', models.BooleanField(default=False)),
                ('boosters', models.IntegerField(blank=True, default=0, null=True)),
                ('commission_owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='commissions', to=settings.AUTH_USER_MODEL)),
                ('referred_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='referred_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LedgerEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(max_length=255)),
                ('debit', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('credit', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('user_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('blue_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('boosters_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('master_balance', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('ledger_name', models.CharField(max_length=255)),
                ('is_public', models.BooleanField(default=False)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Ledger Record',
            },
        ),
        migrations.CreateModel(
            name='BoosterProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BoosterNumbers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
# Generated manually for the mini-project package.
from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160)),
                ('property_type', models.CharField(choices=[('FLAT', 'Flat'), ('BUNGALOW', 'Bungalow'), ('PLOT', 'Plot'), ('SHOP', 'Shop'), ('OFFICE', 'Office')], max_length=20)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('1.00'))])),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=80)),
                ('area_sqft', models.PositiveIntegerField(default=0)),
                ('bedrooms', models.PositiveIntegerField(default=0)),
                ('bathrooms', models.PositiveIntegerField(default=0)),
                ('cover_image_url', models.URLField(blank=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending Approval'), ('APPROVED', 'Available'), ('REJECTED', 'Rejected'), ('SOLD', 'Sold')], default='PENDING', max_length=20)),
                ('rejection_reason', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='properties', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name_plural': 'Properties', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('BUYER', 'Buyer'), ('SELLER', 'Seller'), ('ADMIN', 'Super Admin')], default='BUYER', max_length=20)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('address', models.TextField(blank=True)),
                ('city', models.CharField(blank=True, max_length=80)),
                ('avatar_url', models.URLField(blank=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BuyerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferred_city', models.CharField(blank=True, max_length=80)),
                ('min_budget', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('max_budget', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='marketplace.property')),
            ],
            options={'ordering': ['-created_at'], 'unique_together': {('buyer', 'property')}},
        ),
        migrations.CreateModel(
            name='Inquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_name', models.CharField(max_length=120)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('NEW', 'New'), ('VIEWED', 'Viewed'), ('RESPONDED', 'Responded')], default='NEW', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inquiries', to=settings.AUTH_USER_MODEL)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inquiries', to='marketplace.property')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seller_inquiries', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name_plural': 'Inquiries', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='PropertyImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField()),
                ('caption', models.CharField(blank=True, max_length=120)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery_images', to='marketplace.property')),
            ],
        ),
        migrations.CreateModel(
            name='SellerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agency_name', models.CharField(blank=True, max_length=120)),
                ('verified', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='seller_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('final_price', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('1.00'))])),
                ('transaction_date', models.DateField()),
                ('status', models.CharField(choices=[('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')], default='IN_PROGRESS', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='purchase_transactions', to=settings.AUTH_USER_MODEL)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='marketplace.property')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sale_transactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-transaction_date', '-created_at']},
        ),
    ]

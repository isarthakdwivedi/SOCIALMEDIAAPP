# Generated by Django 5.2 on 2025-04-09 12:13

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
            name="Profile",
            fields=[
                (
                    "id_user",
                    models.IntegerField(default=0, primary_key=True, serialize=False),
                ),
                ("bio", models.TextField(blank=True, default="")),
                (
                    "profileimg",
                    models.ImageField(
                        default="default-avatar-profile-icon-social-media-user-image-gray-avatar-icon-blank-profile-silhouette-illustration-vector.png",
                        upload_to="profile_images",
                    ),
                ),
                ("location", models.CharField(blank=True, default="", max_length=100)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

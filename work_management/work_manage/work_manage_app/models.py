from django.db import models


class Register(models.Model):
    name = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10)
    password = models.CharField(max_length=128)

    STATUS_CHOICES = (
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Active",
    )

    def __str__(self):
        return self.name

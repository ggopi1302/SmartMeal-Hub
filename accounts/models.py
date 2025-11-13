from django.contrib.auth.models import AbstractUser
from django.db import models


class StudentUser(AbstractUser):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    # --- Basic Info ---
    full_name = models.CharField(max_length=100, blank=True)
    university_name = models.CharField(max_length=150, blank=True)
    student_id = models.CharField(max_length=50, unique=True, help_text="Unique university student ID")
    email = models.EmailField(unique=True, help_text="University email address")

    # --- Demographic Info ---
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    # --- Profile ---
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        default='profile_pics/default_user.png'
    )

    # --- Verification & Status ---
    is_verified_university_email = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

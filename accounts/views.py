from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

StudentUser = get_user_model()


def register(request):
    """Handles student registration — only fields in StudentUser model are saved."""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        gender = request.POST.get("gender")
        age = request.POST.get("age")
        university_name = request.POST.get("university_name", "").strip()
        student_id = request.POST.get("student_id", "").strip()
        profile_picture = request.FILES.get("profile_picture")

        # === Validations ===
        if not email.endswith(".edu"):
            messages.error(request, "Please use your university (.edu) email address.")
            return redirect("accounts:register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("accounts:register")

        if StudentUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("accounts:register")

        if StudentUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("accounts:register")

        if StudentUser.objects.filter(student_id=student_id).exists():
            messages.error(request, "Student ID already registered.")
            return redirect("accounts:register")

        # Convert age safely
        age_value = int(age) if age else None

        # === Create User ===
        user = StudentUser.objects.create_user(
            username=username,
            password=password,
            full_name=full_name,
            email=email,
            gender=gender,
            age=age_value,
            university_name=university_name,
            student_id=student_id,
            is_verified_university_email=True
        )

        # Add profile picture if uploaded
        if profile_picture:
            user.profile_picture = profile_picture
            user.save()

        messages.success(request, "🎉 Account created successfully! You can now log in.")
        return redirect("accounts:login")

    return render(request, "register.html")


def login_view(request):
    """Handles student login using username and password."""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.full_name or user.username}!")
            return redirect("accounts:home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("accounts:login")

    return render(request, "login.html")


def logout_view(request):
    """Logs out the user."""
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("accounts:login")


@login_required
def index(request):
    """Home page view."""
    return render(request, "index.html")


@login_required
def profile_view(request):
    """Display logged-in student's profile information."""
    user = request.user

    context = {
        "user": user,
    }
    return render(request, "profile.html", context)

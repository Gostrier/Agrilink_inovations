from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile

# Register
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            return render(request, "register.html", {"error": "Passwords do not match"})
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already exists"})

        user = User.objects.create_user(username=username, email=email, password=password1)
        Profile.objects.create(user=user)  # create blank profile
        return redirect("login")

    return render(request, "register.html")

# Login
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")

# Logout
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def profile_view(request):
    """Allow user to view and update their own profile"""
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        bio = request.POST.get("bio")
        profile.bio = bio
        if "profile_pic" in request.FILES:
            profile.profile_pic = request.FILES["profile_pic"]
        profile.save()
        return redirect("profile")

    return render(request, "profile.html", {"profile": profile})


@login_required
def public_profile_view(request, username):
    """Allow users to view another user's profile"""
    profile = get_object_or_404(Profile, user__username=username)
    return render(request, "public_profile.html", {"profile": profile})

@login_required
def community_view(request):
    """Show all registered users with their profiles"""
    profiles = Profile.objects.select_related("user").all()
    return render(request, "community.html", {"profiles": profiles})
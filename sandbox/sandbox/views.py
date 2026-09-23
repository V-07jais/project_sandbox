from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Projectt

# Homepage
def home(request):
    return render(request, "index.html")   # or homepage.html, choose ONE

# About page
def about(request):
    return render(request, "about.html")   # better than HttpResponse

# Courses list
def courses(request):
    return render(request, "courses.html")  # better than hardcoded HTML

# Single course details
def course_detail(request, courseid):
    return HttpResponse(f"Course ID: {courseid}")   # later replace with template

# Show all projects
def projects(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        link = request.POST.get("link")

        if title and description:
            # Agar user logged in hai toh associate hoga, varna basic setup ke liye default
            user = request.user if request.user.is_authenticated else None
            if user:
                Project.objects.create(
                    user=user,
                    title=title,
                    description=description,
                    link=link
                )
                return redirect('/')

    return render(request, "projects.html")

# Show single project
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, "project_detail.html", {"project": project})

# Login
def login_page(request):
    return render(request, "login.html")

# Profile
def profile_page(request):
    return render(request, "profile.html")

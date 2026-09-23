from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Profile, Comment

# Homepage
def index(request):
    latest_projects = Project.objects.all().order_by('-created_at')[:6]
    return render(request, "index.html", {"projects": latest_projects})

# All Projects Page (Search + Sorting including Most Popular)
def projects(request):
    sort = request.GET.get('sort', 'newest')
    query = request.GET.get('q', '')

    all_projects = Project.objects.all()

    if query:
        all_projects = all_projects.filter(title__icontains=query) | \
                       all_projects.filter(description__icontains=query) | \
                       all_projects.filter(tech_stack__icontains=query)

    if sort == 'oldest':
        all_projects = all_projects.order_by('created_at')
    elif sort == 'popular':
        all_projects = all_projects.annotate(likes_count=models.Count('likes')).order_by('-likes_count', '-created_at')
    else:
        all_projects = all_projects.order_by('-created_at')

    context = {
        'projects': all_projects,
        'current_sort': sort,
        'query': query
    }
    return render(request, "projects.html", context)

# Add Project View
@login_required(login_url='/login/')
def add_project(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        tech_stack = request.POST.get("tech_stack", "").strip()
        link = request.POST.get("link", "").strip()

        if link and not (link.startswith("http://") or link.startswith("https://")):
            link = "https://" + link

        if title and description:
            Project.objects.create(
                user=request.user,
                title=title,
                description=description,
                tech_stack=tech_stack,
                link=link
            )
            messages.success(request, "Project successfully published!")
            return redirect('/profile/')

    return render(request, "add_project.html")

# Edit Project View
@login_required(login_url='/login/')
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.user != request.user:
        messages.error(request, "You are not authorized to edit this project.")
        return redirect('/projects/')

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        tech_stack = request.POST.get("tech_stack", "").strip()
        link = request.POST.get("link", "").strip()

        if link and not (link.startswith("http://") or link.startswith("https://")):
            link = "https://" + link

        if title and description:
            project.title = title
            project.description = description
            project.tech_stack = tech_stack
            project.link = link
            project.save()
            messages.success(request, "Project updated successfully!")
            return redirect(f'/project/{project.id}/')

    return render(request, "edit_project.html", {"project": project})

# Delete Project View
@login_required(login_url='/login/')
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.user != request.user:
        messages.error(request, "You are not authorized to delete this project.")
        return redirect('/projects/')

    project.delete()
    messages.success(request, "Project deleted successfully.")
    return redirect('/profile/')

# Like / Upvote View
@login_required(login_url='/login/')
def like_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.likes.filter(id=request.user.id).exists():
        project.likes.remove(request.user)
    else:
        project.likes.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', '/projects/'))

# Add Comment View
@login_required(login_url='/login/')
def add_comment(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if text:
            Comment.objects.create(
                project=project,
                user=request.user,
                text=text
            )
            messages.success(request, "Comment added successfully!")
    return redirect(f'/project/{project.id}/')

# Project Detail View
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    comments = project.comments.all().order_by('-created_at')
    return render(request, "project_detail.html", {"project": project, "comments": comments})

# Profile View
@login_required(login_url='/login/')
def profile_page(request):
    my_projects = Project.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "profile.html", {'my_projects': my_projects})

# Edit Profile View
@login_required(login_url='/login/')
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        bio = request.POST.get("bio", "").strip()
        skills = request.POST.get("skills", "").strip()
        github_url = request.POST.get("github_url", "").strip()
        linkedin_url = request.POST.get("linkedin_url", "").strip()

        if github_url and not (github_url.startswith("http://") or github_url.startswith("https://")):
            github_url = "https://" + github_url
        if linkedin_url and not (linkedin_url.startswith("http://") or linkedin_url.startswith("https://")):
            linkedin_url = "https://" + linkedin_url

        profile.bio = bio
        profile.skills = skills
        profile.github_url = github_url
        profile.linkedin_url = linkedin_url
        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('/profile/')

    return render(request, "edit_profile.html", {"profile": profile})

# Auth Views
def signup_page(request):
    if request.user.is_authenticated:
        return redirect('/profile/')
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, "signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, "signup.html")

        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user)
        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect('/profile/')
    return render(request, "signup.html")

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/profile/')
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('/profile/')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "login.html")

def logout_user(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('/')
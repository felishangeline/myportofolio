from django.contrib import messages
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

import datetime

from main.forms import (
    SkillForm, 
    ExperienceForm,
    )

from main.models import (
    Experience, 
    Skills,
    )

def get_skills_json(request):
    title_query = request.GET.get("title", "").strip()
    skills = Skills.objects.all()

    if title_query:
        skills = skills.filter(title__icontains=title_query)

    skills_json = serializers.serialize("json", skills, use_natural_foreign_keys=True)
    return HttpResponse(skills_json, content_type="application/json")

@login_required(login_url="/login/")
def create_skills(request):
    form = SkillForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_skills")

    context = {
        "name": "Felisha Angeline",
        "form": form,
    }
    return render(request, "skills_form.html", context)

def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login/Cookie tidak ditemukan')

    context = {
        "name": "Felisha Angeline",
        "npm": "2506656740",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "A Computer Science Student at Universitas Indonesia who is a strong believer of work-life balance."
            "Weekdays I'm in Depok while weekends are reserved for badminton, pilates, hangouts, and mall-hopping."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Felisha Angeline",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_skills(request):
    title_query = request.GET.get("title", "").strip()

    context = {
        "name" : "Felisha Angeline",
        "title_query": title_query,
        "form": SkillForm(),
    }
    return render(request, "skills.html", context)

@login_required(login_url="/login/")
def delete_skill(request, skill_id):
    skills = get_object_or_404(Skills, pk=skill_id)

    if request.method == "POST":
        skills.delete()
        messages.success(request, "Skill berhasil dihapus!")
        return redirect("main:show_skills")

    return redirect("main:show_skills")

@login_required(login_url="/login/")
def edit_skill(request, skill_id):
    skills = get_object_or_404(Skills, pk=skill_id)
    form = SkillForm(request.POST or None, instance=skills)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill berhasil diupdate!")
        return redirect("main:show_skills")

    context = {
        "name": "Felisha Angeline",
        "form": form,
        "skills": skills,
    }
    return render(request, "skills_form.html", context)

@login_required(login_url="/login/")
def create_experience(request):
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": "Felisha Angeline",
        "form": form,
    }
    return render(request, "experience_form.html", context)

@login_required(login_url="/login/")
def edit_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman berhasil diupdate!")
        return redirect("main:show_experience")

    context = {
        "name": "Felisha Angeline",
        "form": form,
        "experience": experience,
    }
    return render(request, "experience_form.html", context)

@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        experience.delete()
        messages.success(request, "Pengalaman berhasil dihapus!")
    return redirect("main:show_experience")

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silahkan login.")
        return redirect("main:login")

    context = {
        "name": "Felisha Angeline",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        auth_login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Felisha Angeline",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

@login_required(login_url="/login/")
def toggle_skill_star(request, skill_id):
    skill = get_object_or_404(Skills, pk=skill_id)

    if request.method == "POST":
        if request.user in skill.starred_by.all():
            skill.starred_by.remove(request.user)
        else:
            skill.starred_by.add(request.user)

    return redirect("main:show_skills")

@login_required(login_url="/login/")
def toggle_experience_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        if request.user in experience.starred_by.all():
            experience.starred_by.remove(request.user)
        else:
            experience.starred_by.add(request.user)

    return redirect("main:show_experience")

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    skills = Skills.objects.prefetch_related('starred_by').all()

    if title_query:
        skills = skills.filter(title_icontains=title_query)

    data = []
    for skill in skills:
        starred_users = skill.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(skill.id),
            "fields": {
                "title": skill.title,
                "description": skill.description,
                "skill_gained": skill.skill_gained,
                "skill_level": skill.skill_level,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })

    return JsonResponse(data, safe=False)

@require_POST
def create_skill_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan skill."},
            status = 403,
        )
    
    form = SkillForm(request.POST)
    if form.is_valid():
        skill = form.save()
        return JsonResponse(
            {"message": "Skill berhasil ditambahkan.", "pk": str(skill.id)},
            status = 201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status = 400)
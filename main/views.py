from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import SkillForm
from main.models import Experience

from main.models import Skills

def get_skills_json(request):
    title_query = request.GET.get("title", "").strip()
    skills = Skills.objects.all()

    if title_query:
        skills = skills.filter(title__icontains=title_query)

    skills_json = serializers.serialize("json", skills)
    return HttpResponse(skills_json, content_type="application/json")
    

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
    context = {
        "name": "Felisha Angeline",
        "npm": "2506656740",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "A Computer Science Student at Universitas Indonesia who is a strong believer of work-life balance."
            "Weekdays I'm in Depok while weekends are reserved for badminton, pilates, hangouts, and mall-hopping."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Felisha Angeline",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_skills(request):
    json_response = get_skills_json(request)

    skills = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    skills = [skills.object for skills in skills]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name" : "Felisha Angeline",
        "skill_list": skills,
        "title_query": title_query,
    }
    return render(request, "skills.html", context)

def delete_skills(request, skills_id):
    skills = get_object_or_404(Skills, pk=skills_id)

    if request.method == "POST":
        skills.delete()
        messages.success(request, "Skill berhasil dihapus!")
        return redirect("main:show_skills")

    return redirect("main:show_skills")

def edit_skills(request, skills_id):
    skills = get_object_or_404(Skills, pk=skills_id)
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
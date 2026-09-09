from django.shortcuts import render

from main.models import Experience


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
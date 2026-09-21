from django.urls import path

from main.views import (
    delete_skills, 
    get_skills_json, 
    show_main, 
    show_experience, 
    show_skills, 
    create_skills,
    edit_skills,
    )

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("skills/", show_skills, name="show_skills"),
    path("skills/add/", create_skills, name="create_skills"),
    path("api/skills/", get_skills_json, name="get_skills_json"),
    path("skills/<uuid:skills_id>/delete/",delete_skills,name="delete_skills"),
    path("skills/<uuid:skills_id>/edit/", edit_skills, name="edit_skills"),
]
from django.urls import path

from main.views import (
    delete_skills, 
    get_skills_json, 
    show_main, 
    show_experience, 
    show_skills, 
    create_skills,
    edit_skills,
    create_experience,
    edit_experience,
    delete_experience,
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
    path("experience/", show_experience, name="show_experience"),
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/<uuid:experience_id>/edit/", edit_experience, name="edit_experience"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
]
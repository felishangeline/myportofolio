from django.forms import ModelForm, TextInput, Textarea, URLInput, DateTimeInput

from main.models import Skills, Experience, Project

class SkillForm(ModelForm):
    class Meta:
        model = Skills
        fields = [
            "title",
            "description",
            "skill_gained",
            "skill_level",
        ]

        labels = {
            "title": "Nama Skill",
            "description": "Deskripsi Skill",
            "skill_gained": "dimana mendapatkan skill",
            "skill_level": "level skill yang dimiliki",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "desc skills",
                    "rows": 3,
                }
            ),
            "skill_gained": TextInput(
                attrs={
                    "placeholder": "where it was gained",
                }
            ),

            "skill_level": TextInput(
                attrs = {
                    "placeholder": "beginner, advanced, intermediate",
                }
            ),
        }

class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
            "ended_at",
        ]
        
        widgets = {
            "title": TextInput(attrs={"placeholder": "Software Engineering Intern"}),
            "description": Textarea(attrs={"placeholder": "Deskripsikan pengalamanmu...", "rows": 3}),
            "thumbnail": URLInput(attrs={"placeholder": "https://example.com/image.jpg"}),
            "ended_at": DateTimeInput(attrs={"type": "datetime-local"}),
        }

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/kakBurhan/burhanquestv4",
                }
            ),
            "project_image_url": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
        }
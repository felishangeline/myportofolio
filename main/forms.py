from django.forms import ModelForm, TextInput, Textarea, URLInput, DateTimeInput

from main.models import Skills, Experience

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
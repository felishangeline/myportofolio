from django.forms import ModelForm, TextInput, Textarea, URLInput

from main.models import Skills

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
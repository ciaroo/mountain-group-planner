from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "display_name",
            "allergies",
            "food_preferences",
            "has_car",
            "car_model",
            "car_seats",
            "notes",
        ]

        widgets = {
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
            "allergies": forms.Textarea(attrs={"class": "form-control"}),
            "food_preferences": forms.Textarea(attrs={"class": "form-control"}),
            "has_car": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "car_model": forms.TextInput(attrs={"class": "form-control"}),
            "car_seats": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control"}),
        }
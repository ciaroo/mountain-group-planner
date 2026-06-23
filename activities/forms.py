from django import forms

from .models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = [
            "title",
            "category",
            "description",
            "date",
            "start_time",
            "end_time",
            "meeting_place",
            "max_participants",
            "what_to_bring",
        ]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "meeting_place": forms.TextInput(attrs={"class": "form-control"}),
            "max_participants": forms.NumberInput(attrs={"class": "form-control"}),
            "what_to_bring": forms.Textarea(attrs={"class": "form-control"}),
        }
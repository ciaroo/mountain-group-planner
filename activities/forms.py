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

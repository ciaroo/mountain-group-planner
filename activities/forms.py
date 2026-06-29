from django import forms

from .models import Activity, Notice


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = [
            "title",
            "category",
            "description",
            "image",
            "date",
            "start_time",
            "end_time",
            "meeting_place",
            "max_participants",
            "price",
            "what_to_bring",
            "requires_booking",
        ]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "meeting_place": forms.TextInput(attrs={"class": "form-control"}),
            "max_participants": forms.NumberInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "Es. 25.00"
                }
            ),
            "what_to_bring": forms.Textarea(attrs={"class": "form-control"}),
            "requires_booking": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

        labels = {
            "price": "Prezzo",
        }

        help_texts = {
            "price": "Lascia vuoto se l'attività è gratuita o se il prezzo non è previsto.",
        }

    def clean(self):
        cleaned_data = super().clean()

        requires_booking = cleaned_data.get("requires_booking")
        max_participants = cleaned_data.get("max_participants")

        if requires_booking and not max_participants:
            self.add_error(
                "max_participants",
                "Inserisci il numero massimo di partecipanti per le attività prenotabili."
            )

        return cleaned_data


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = [
            "title",
            "content",
            "priority",
            "is_active",
        ]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
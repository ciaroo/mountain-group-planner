from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        label="Nome",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    last_name = forms.CharField(
        label="Cognome",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    birth_date = forms.DateField(
        label="Data di nascita",
        required=True,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"})
    )

    birth_place = forms.CharField(
        label="Luogo di nascita",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    residence_place = forms.CharField(
        label="Luogo di residenza",
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    residence_address = forms.CharField(
        label="Via / indirizzo di residenza",
        max_length=250,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    sex = forms.ChoiceField(
        label="Sesso",
        required=True,
        choices=Profile.SEX_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    document_type = forms.ChoiceField(
        label="Tipo di documento",
        required=True,
        choices=Profile.DOCUMENT_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    document_number = forms.CharField(
        label="Numero documento",
        max_length=80,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    document_issuing_authority = forms.CharField(
        label="Ente rilascio documento",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    wants_linen_rental = forms.BooleanField(
        label="Voglio noleggiare la biancheria al costo di 15€",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    invite_code = forms.CharField(
        label="Codice invito",
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "birth_date",
            "birth_place",
            "residence_place",
            "residence_address",
            "sex",
            "document_type",
            "document_number",
            "document_issuing_authority",
            "wants_linen_rental",
            "invite_code",
        ]

        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Nome utente"
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Conferma password"

        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

        self.fields["username"].help_text = ""
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Esiste già un account con questa email.")

        return email

    def clean_invite_code(self):
        invite_code = self.cleaned_data.get("invite_code")

        if invite_code != settings.REGISTRATION_INVITE_CODE:
            raise forms.ValidationError("Codice invito non valido.")

        return invite_code

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

            profile_obj, created = Profile.objects.get_or_create(
                user=user
            )

            profile_obj.display_name = f"{user.first_name} {user.last_name}".strip()
            profile_obj.birth_date = self.cleaned_data["birth_date"]
            profile_obj.birth_place = self.cleaned_data["birth_place"]
            profile_obj.residence_place = self.cleaned_data["residence_place"]
            profile_obj.residence_address = self.cleaned_data["residence_address"]
            profile_obj.sex = self.cleaned_data["sex"]
            profile_obj.document_type = self.cleaned_data["document_type"]
            profile_obj.document_number = self.cleaned_data["document_number"]
            profile_obj.document_issuing_authority = self.cleaned_data["document_issuing_authority"]
            profile_obj.wants_linen_rental = self.cleaned_data["wants_linen_rental"]
            profile_obj.save()

        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "display_name",
            "birth_date",
            "birth_place",
            "residence_place",
            "residence_address",
            "sex",
            "document_type",
            "document_number",
            "document_issuing_authority",
            "wants_linen_rental",
            "allergies",
            "food_preferences",
            "has_car",
            "car_seats",
            "notes",
        ]

        widgets = {
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
            "birth_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "birth_place": forms.TextInput(attrs={"class": "form-control"}),
            "residence_place": forms.TextInput(attrs={"class": "form-control"}),
            "residence_address": forms.TextInput(attrs={"class": "form-control"}),
            "sex": forms.Select(attrs={"class": "form-select"}),
            "document_type": forms.Select(attrs={"class": "form-select"}),
            "document_number": forms.TextInput(attrs={"class": "form-control"}),
            "document_issuing_authority": forms.TextInput(attrs={"class": "form-control"}),
            "wants_linen_rental": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "allergies": forms.Textarea(attrs={"class": "form-control"}),
            "food_preferences": forms.Textarea(attrs={"class": "form-control"}),
            "has_car": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "car_seats": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control"}),
        }

        labels = {
            "wants_linen_rental": "Voglio noleggiare la biancheria al costo di 15€",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = [
            "display_name",
            "birth_date",
            "birth_place",
            "residence_place",
            "residence_address",
            "sex",
            "document_type",
            "document_number",
            "document_issuing_authority",
        ]

        for field_name in required_fields:
            self.fields[field_name].required = True
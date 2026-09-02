from django import forms
from .models import TenderDocument


class TenderDocumentForm(forms.ModelForm):

    class Meta:
        model = TenderDocument

        fields = [
            "title",
            "file",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter document title",
                }
            ),

            "file": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf",
                }
            ),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")

        if uploaded_file:

            if not uploaded_file.name.lower().endswith(".pdf"):
                raise forms.ValidationError(
                    "Only PDF files are allowed."
                )

        return uploaded_file
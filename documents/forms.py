from django import forms

from .models import (
    ProjectSolution,
    Requirement,
    TenderDocument,
)


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

            "file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf",
                }
            ),

        }


class ProjectSolutionForm(forms.ModelForm):

    class Meta:

        model = ProjectSolution

        fields = [
            "title",
            "description",
        ]

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter solution title",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Describe your proposed solution in detail"
                    ),
                    "rows": 8,
                }
            ),

        }


class RequirementForm(forms.ModelForm):

    class Meta:

        model = Requirement

        fields = [
            "category",
            "requirement_text",
            "is_mandatory",
        ]

        widgets = {

            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "requirement_text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Enter tender requirement"
                    ),
                    "rows": 4,
                }
            ),

            "is_mandatory": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

        }
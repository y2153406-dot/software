from django.db import models

from projects.models import Project


class TenderDocument(models.Model):

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="tender_document",
    )

    title = models.CharField(
        max_length=255,
    )

    file = models.FileField(
        upload_to="tender_documents/",
    )

    extracted_text = models.TextField(
        blank=True,
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):

        return self.title


class Requirement(models.Model):

    CATEGORY_CHOICES = [
        ("technical", "Technical"),
        ("financial", "Financial"),
        ("eligibility", "Eligibility"),
        ("legal", "Legal"),
        ("other", "Other"),
    ]

    document = models.ForeignKey(
        TenderDocument,
        on_delete=models.CASCADE,
        related_name="requirements",
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="other",
    )

    requirement_text = models.TextField()

    is_mandatory = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):

        return self.requirement_text[:100]


class ProjectSolution(models.Model):

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="solution",
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):

        return self.title


class ComplianceResult(models.Model):

    STATUS_CHOICES = [
        ("compliant", "Compliant"),
        ("partial", "Partially Compliant"),
        ("non_compliant", "Non-Compliant"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="compliance_results",
    )

    requirement = models.ForeignKey(
        Requirement,
        on_delete=models.CASCADE,
        related_name="compliance_results",
    )

    solution = models.ForeignKey(
        ProjectSolution,
        on_delete=models.CASCADE,
        related_name="compliance_results",
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="non_compliant",
    )

    confidence_score = models.FloatField(
        default=0,
    )

    explanation = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):

        return (
            f"Requirement {self.requirement.id} - "
            f"{self.status}"
        )

class RiskAnalysis(models.Model):

    RISK_LEVEL_CHOICES = [
        ("low", "Low Risk"),
        ("medium", "Medium Risk"),
        ("high", "High Risk"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="risk_analyses",
    )

    requirement = models.ForeignKey(
        Requirement,
        on_delete=models.CASCADE,
        related_name="risk_analyses",
    )

    solution = models.ForeignKey(
        ProjectSolution,
        on_delete=models.CASCADE,
        related_name="risk_analyses",
    )

    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL_CHOICES,
        default="medium",
    )

    risk_score = models.FloatField(
        default=0,
    )

    explanation = models.TextField()

    recommendation = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):

        return (
            f"{self.requirement.id} - "
            f"{self.risk_level}"
        )
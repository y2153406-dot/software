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
from django.shortcuts import get_object_or_404, redirect, render

from projects.models import Project
from .forms import TenderDocumentForm
from .utils import extract_text_from_pdf


def tender_document_upload(request, project_id):
    project = get_object_or_404(
        Project,
        id=project_id,
    )

    # Prevent duplicate main tender document
    if hasattr(project, "tender_document"):
        return redirect("project_list")

    if request.method == "POST":
        form = TenderDocumentForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            tender_document = form.save(
                commit=False,
            )

            tender_document.project = project
        tender_document.save()

        extracted_text = extract_text_from_pdf(
            tender_document.file.path
        )

        tender_document.extracted_text = extracted_text
        tender_document.save()

        return redirect("project_list")
    else:
        form = TenderDocumentForm()

    return render(
        request,
        "documents/tender_document_upload.html",
        {
            "form": form,
            "project": project,
        },
    )
from django.urls import path
from . import views


urlpatterns = [

    path(
        "project/<int:project_id>/upload-tender/",
        views.tender_document_upload,
        name="tender_document_upload",
    ),

    path(
        "document/<int:document_id>/extract-requirements/",
        views.extract_tender_requirements,
        name="extract_tender_requirements",
    ),

    path(
        "project/<int:project_id>/solution/",
        views.project_solution,
        name="project_solution",
    ),

    path(
        "project/<int:project_id>/analyze-compliance/",
        views.analyze_project_compliance,
        name="analyze_project_compliance",
    ),

    path(
        "project/<int:project_id>/compliance-report/",
        views.compliance_report,
        name="compliance_report",
    ),
    path(
    "project/<int:project_id>/analyze-risks/",
    views.analyze_project_risks,
    name="analyze_project_risks",
),
    path(
    "project/<int:project_id>/download-compliance-report/",
    views.download_compliance_report_pdf,
    name="download_compliance_report_pdf",
),

]
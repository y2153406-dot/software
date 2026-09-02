from django.urls import path
from . import views


urlpatterns = [
    path(
        "project/<int:project_id>/upload-tender/",
        views.tender_document_upload,
        name="tender_document_upload",
    ),
]
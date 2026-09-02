from django.shortcuts import render, redirect
from .models import Project
from .forms import ProjectForm


def project_list(request):
    projects = Project.objects.all().order_by("-created_at")

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": projects,
        },
    )


def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("project_list")

    else:
        form = ProjectForm()

    return render(
        request,
        "projects/project_form.html",
        {
            "form": form,
        },
    )
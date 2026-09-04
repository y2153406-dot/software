from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import ProjectForm
from .models import Project

from documents.models import (
    ComplianceResult,
    ProjectSolution,
    Requirement,
    RiskAnalysis,
    TenderDocument,
)


def project_list(request):

    projects = Project.objects.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": projects,
        },
    )


def project_create(request):

    if request.method == "POST":

        form = ProjectForm(
            request.POST
        )

        if form.is_valid():

            project = form.save()

            return redirect(
                "project_dashboard",
                project_id=project.id,
            )

    else:

        form = ProjectForm()

    return render(
        request,
        "projects/project_form.html",
        {
            "form": form,
        },
    )


def project_dashboard(
    request,
    project_id,
):

    project = get_object_or_404(
        Project,
        id=project_id,
    )


    # Tender document

    tender_document = (
        TenderDocument.objects.filter(
            project=project
        )
        .order_by(
            "-uploaded_at"
        )
        .first()
    )


    # Requirements

    total_requirements = (
        Requirement.objects.filter(
            document__project=project
        ).count()
    )


    # Project solution

    solution = (
        ProjectSolution.objects.filter(
            project=project
        ).first()
    )


    # Compliance results

    compliance_results = (
        ComplianceResult.objects.filter(
            project=project
        )
    )


    compliant_count = (
        compliance_results.filter(
            status="compliant"
        ).count()
    )


    partial_count = (
        compliance_results.filter(
            status="partial"
        ).count()
    )


    non_compliant_count = (
        compliance_results.filter(
            status="non_compliant"
        ).count()
    )


    # Overall compliance score

    overall_score = 0


    if compliance_results.exists():

        total_score = 0


        for result in compliance_results:

            if result.status == "compliant":

                total_score += 100


            elif result.status == "partial":

                total_score += 50


        overall_score = round(
            total_score
            / compliance_results.count()
        )


    # Risk analysis

    risk_results = (
        RiskAnalysis.objects.filter(
            project=project
        )
    )


    total_risks = (
        risk_results.count()
    )


    high_risk_count = (
        risk_results.filter(
            risk_level="high"
        ).count()
    )


    return render(
        request,
        "projects/project_dashboard.html",
        {
            "project": project,

            "tender_document": tender_document,

            "total_requirements": total_requirements,

            "solution": solution,

            "compliant_count": compliant_count,

            "partial_count": partial_count,

            "non_compliant_count": non_compliant_count,

            "overall_score": overall_score,

            "total_risks": total_risks,

            "high_risk_count": high_risk_count,
        },
    )
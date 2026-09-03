from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from projects.models import Project

from .ai_services import (
    extract_requirements_with_ai,
)

from .compliance_ai import (
    analyze_compliance,
)

from .fallback_compliance import (
    analyze_compliance_fallback,
)

from .fallback_risk import (
    analyze_risks_fallback,
)

from .forms import (
    ProjectSolutionForm,
    RequirementForm,
    TenderDocumentForm,
)

from .models import (
    ComplianceResult,
    ProjectSolution,
    Requirement,
    RiskAnalysis,
    TenderDocument,
)

from .risk_ai import (
    analyze_risks,
)

from .utils import (
    extract_text_from_pdf,
)

def tender_document_upload(request, project_id):

    project = get_object_or_404(
        Project,
        id=project_id,
    )

    tender_document = TenderDocument.objects.filter(
        project=project
    ).first()

    if request.method == "POST":

        if tender_document:

            return redirect(
                "tender_document_upload",
                project_id=project.id,
            )

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

            return redirect(
                "tender_document_upload",
                project_id=project.id,
            )

    else:

        form = TenderDocumentForm()

    return render(
        request,
        "documents/tender_document_upload.html",
        {
            "form": form,
            "project": project,
            "tender_document": tender_document,
        },
    )


def extract_tender_requirements(request, document_id):

    document = get_object_or_404(
        TenderDocument,
        id=document_id,
    )

    if request.method != "POST":

        return redirect(
            "tender_document_upload",
            project_id=document.project.id,
        )

    if not document.extracted_text:

        return redirect(
            "tender_document_upload",
            project_id=document.project.id,
        )

    document.requirements.all().delete()

    result = extract_requirements_with_ai(
        document.extracted_text
    )

    for item in result.get(
        "requirements",
        [],
    ):

        Requirement.objects.create(
            document=document,
            category=item.get(
                "category",
                "other",
            ),
            requirement_text=item.get(
                "requirement_text",
                "",
            ),
            is_mandatory=item.get(
                "is_mandatory",
                True,
            ),
        )

    return redirect(
        "tender_document_upload",
        project_id=document.project.id,
    )

def project_solution(request, project_id):

    project = get_object_or_404(
        Project,
        id=project_id,
    )

    solution = ProjectSolution.objects.filter(
        project=project
    ).first()

    if request.method == "POST":

        form = ProjectSolutionForm(
            request.POST,
            instance=solution,
        )

        if form.is_valid():

            solution = form.save(
                commit=False,
            )

            solution.project = project

            solution.save()

            return redirect(
                "project_solution",
                project_id=project.id,
            )

    else:

        form = ProjectSolutionForm(
            instance=solution,
        )

    # Get compliance results
    compliance_results = ComplianceResult.objects.filter(
        project=project
    ).select_related(
        "requirement"
    )
    risk_results = RiskAnalysis.objects.filter(
    project=project,
    solution=solution,
).select_related(
    "requirement"
)
    # Dashboard counts
    total_requirements = compliance_results.count()

    compliant_count = compliance_results.filter(
        status="compliant"
    ).count()

    partial_count = compliance_results.filter(
        status="partial"
    ).count()

    non_compliant_count = compliance_results.filter(
        status="non_compliant"
    ).count()

    # Calculate overall compliance score
    overall_score = 0

    if total_requirements > 0:

        total_score = 0

        for result in compliance_results:

            if result.status == "compliant":

                total_score += 100

            elif result.status == "partial":

                total_score += 50

            else:

                total_score += 0

        overall_score = round(
            total_score / total_requirements
        )

    # Tender readiness status
    readiness_status = "Not Analyzed"
    readiness_class = "secondary"

    if total_requirements > 0:

        if overall_score >= 80:

            readiness_status = "Excellent"
            readiness_class = "success"

        elif overall_score >= 60:

            readiness_status = "Good"
            readiness_class = "primary"

        elif overall_score >= 40:

            readiness_status = "Needs Improvement"
            readiness_class = "warning"

        else:

            readiness_status = "High Risk"
            readiness_class = "danger"

    return render(
        request,
        "documents/project_solution.html",
        {
            "project": project,
            "form": form,
            "solution": solution,

            "compliance_results": compliance_results,

            "total_requirements": total_requirements,

            "compliant_count": compliant_count,

            "partial_count": partial_count,

            "non_compliant_count": non_compliant_count,

            "overall_score": overall_score,

            "readiness_status": readiness_status,

            "readiness_class": readiness_class,
            "risk_results": risk_results,
        },
    )
def analyze_project_compliance(request, project_id):

    project = get_object_or_404(
        Project,
        id=project_id,
    )

    if request.method != "POST":

        return redirect(
            "project_solution",
            project_id=project.id,
        )

    solution = get_object_or_404(
        ProjectSolution,
        project=project,
    )

    document = get_object_or_404(
        TenderDocument,
        project=project,
    )

    requirements = document.requirements.all()

    if not requirements.exists():

        return redirect(
            "project_solution",
            project_id=project.id,
        )

    try:

        # First try Gemini AI
        try:

            analysis_result = analyze_compliance(
                requirements,
                solution.description,
            )

            print(
                "GEMINI AI ANALYSIS SUCCESSFUL"
            )

        # If Gemini fails, use fallback system
        except Exception as error:

            print(
                "AI ANALYSIS FAILED."
            )

            print(
                "USING FALLBACK SYSTEM:",
                error,
            )

            analysis_result = analyze_compliance_fallback(
                requirements,
                solution.description,
            )

            print(
                "FALLBACK ANALYSIS SUCCESSFUL"
            )

    except Exception as error:

        print(
            "COMPLIANCE ANALYSIS ERROR:",
            error,
        )

        form = ProjectSolutionForm(
            instance=solution,
        )

        return render(
            request,
            "documents/project_solution.html",
            {
                "project": project,
                "solution": solution,
                "form": form,
                "error_message": (
                    "Compliance analysis could not be completed. "
                    "Please try again."
                ),
            },
        )

    results = analysis_result.get(
        "results",
        [],
    )

    # Delete old results only after analysis succeeds
    ComplianceResult.objects.filter(
        project=project
    ).delete()

    # Save new results
    for item in results:

        requirement_id = item.get(
            "requirement_id"
        )

        try:

            requirement = requirements.get(
                id=requirement_id
            )

        except Requirement.DoesNotExist:

            continue

        ComplianceResult.objects.create(
            project=project,
            solution=solution,
            requirement=requirement,
            status=item.get(
                "status",
                "non_compliant",
            ),
            confidence_score=item.get(
                "confidence_score",
                0,
            ),
            explanation=item.get(
                "explanation",
                "",
            ),
        )

    return redirect(
        "project_solution",
        project_id=project.id,
    )

def compliance_report(request, project_id):

    project = get_object_or_404(
        Project,
        id=project_id,
    )

    solution = get_object_or_404(
        ProjectSolution,
        project=project,
    )

    compliance_results = ComplianceResult.objects.filter(
        project=project,
        solution=solution,
    ).select_related(
        "requirement"
    )

    total_requirements = compliance_results.count()

    compliant_count = compliance_results.filter(
        status="compliant"
    ).count()

    partial_count = compliance_results.filter(
        status="partial"
    ).count()

    non_compliant_count = compliance_results.filter(
        status="non_compliant"
    ).count()

    overall_score = 0

    if total_requirements > 0:

        total_score = 0

        for result in compliance_results:

            if result.status == "compliant":

                total_score += 100

            elif result.status == "partial":

                total_score += 50

        overall_score = round(
            total_score / total_requirements
        )

    return render(
        request,
        "documents/compliance_report.html",
        {
            "project": project,
            "solution": solution,
            "compliance_results": compliance_results,
            "total_requirements": total_requirements,
            "compliant_count": compliant_count,
            "partial_count": partial_count,
            "non_compliant_count": non_compliant_count,
            "overall_score": overall_score,
        },
    )

def add_requirement(request, document_id):

    document = get_object_or_404(
        TenderDocument,
        id=document_id,
    )

    if request.method == "POST":

        form = RequirementForm(
            request.POST
        )

        if form.is_valid():

            requirement = form.save(
                commit=False
            )

            requirement.document = document

            requirement.save()

            return redirect(
                "tender_document_upload",
                project_id=document.project.id,
            )

    else:

        form = RequirementForm()

    return render(
        request,
        "documents/requirement_form.html",
        {
            "form": form,
            "document": document,
            "project": document.project,
            "page_title": "Add Requirement",
        },
    )


def edit_requirement(request, requirement_id):

    requirement = get_object_or_404(
        Requirement,
        id=requirement_id,
    )

    document = requirement.document

    if request.method == "POST":

        form = RequirementForm(
            request.POST,
            instance=requirement,
        )

        if form.is_valid():

            form.save()

            return redirect(
                "tender_document_upload",
                project_id=document.project.id,
            )

    else:

        form = RequirementForm(
            instance=requirement,
        )

    return render(
        request,
        "documents/requirement_form.html",
        {
            "form": form,
            "document": document,
            "project": document.project,
            "page_title": "Edit Requirement",
        },
    )


def delete_requirement(request, requirement_id):

    requirement = get_object_or_404(
        Requirement,
        id=requirement_id,
    )

    document = requirement.document

    if request.method == "POST":

        requirement.delete()

    return redirect(
        "tender_document_upload",
        project_id=document.project.id,
    )

def analyze_project_risks(request, project_id):

    project = get_object_or_404(
        Project,
        id=project_id,
    )

    if request.method != "POST":

        return redirect(
            "project_solution",
            project_id=project.id,
        )

    solution = get_object_or_404(
        ProjectSolution,
        project=project,
    )

    document = get_object_or_404(
        TenderDocument,
        project=project,
    )

    requirements = document.requirements.all()

    if not requirements.exists():

        return redirect(
            "project_solution",
            project_id=project.id,
        )

    try:

        # First try Gemini AI

        try:

            analysis_result = analyze_risks(
                requirements,
                solution.description,
            )

            print(
                "GEMINI RISK ANALYSIS SUCCESSFUL"
            )

        # If Gemini fails, use fallback system

        except Exception as error:

            print(
                "AI RISK ANALYSIS FAILED."
            )

            print(
                "USING FALLBACK RISK SYSTEM:",
                error,
            )

            analysis_result = analyze_risks_fallback(
                requirements,
                solution.description,
            )

            print(
                "FALLBACK RISK ANALYSIS SUCCESSFUL"
            )

    except Exception as error:

        print(
            "RISK ANALYSIS ERROR:",
            error,
        )

        form = ProjectSolutionForm(
            instance=solution,
        )

        return render(
            request,
            "documents/project_solution.html",
            {
                "project": project,
                "solution": solution,
                "form": form,
                "error_message": (
                    "Risk analysis could not be completed. "
                    "Please try again."
                ),
            },
        )

    results = analysis_result.get(
        "results",
        [],
    )

    # Delete old risk results only after analysis succeeds

    RiskAnalysis.objects.filter(
        project=project,
        solution=solution,
    ).delete()

    # Save new risk results

    for item in results:

        requirement_id = item.get(
            "requirement_id"
        )

        try:

            requirement = requirements.get(
                id=requirement_id
            )

        except Requirement.DoesNotExist:

            continue

        RiskAnalysis.objects.create(
            project=project,
            solution=solution,
            requirement=requirement,
            risk_level=item.get(
                "risk_level",
                "medium",
            ),
            risk_score=item.get(
                "risk_score",
                0,
            ),
            explanation=item.get(
                "explanation",
                "",
            ),
            recommendation=item.get(
                "recommendation",
                "",
            ),
        )

    return redirect(
        "project_solution",
        project_id=project.id,
    )
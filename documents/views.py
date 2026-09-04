from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from .improvement_ai import (
    generate_improvement_suggestions,
)

from .fallback_improvement import (
    generate_improvement_suggestions_fallback,
)

from .models import (
    ImprovementSuggestion,
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

from django.http import HttpResponse

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
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
        project=project,
    ).select_related(
        "requirement",
    )

    # Get risk analysis results

    risk_results = RiskAnalysis.objects.none()

    if solution:

        risk_results = RiskAnalysis.objects.filter(
            project=project,
            solution=solution,
        ).select_related(
            "requirement",
        )

    # Get improvement suggestions

    improvement_suggestions = (
        ImprovementSuggestion.objects.none()
    )

    if solution:

        improvement_suggestions = (
            ImprovementSuggestion.objects.filter(
                project=project,
                solution=solution,
            ).select_related(
                "requirement",
            )
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

            "compliance_results": (
                compliance_results
            ),

            "risk_results": (
                risk_results
            ),

            "improvement_suggestions": (
                improvement_suggestions
            ),

            "total_requirements": (
                total_requirements
            ),

            "compliant_count": (
                compliant_count
            ),

            "partial_count": (
                partial_count
            ),

            "non_compliant_count": (
                non_compliant_count
            ),

            "overall_score": (
                overall_score
            ),

            "readiness_status": (
                readiness_status
            ),

            "readiness_class": (
                readiness_class
            ),
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
def download_compliance_report_pdf(request, project_id):

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

    # Calculate overall compliance score
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

    # Create PDF response
    response = HttpResponse(
        content_type="application/pdf"
    )

    filename = (
        f"compliance_report_project_{project.id}.pdf"
    )

    response[
        "Content-Disposition"
    ] = f'attachment; filename="{filename}"'

    # Create PDF document
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    elements = []

    styles = getSampleStyleSheet()

    # Title
    elements.append(
        Paragraph(
            "Tender Compliance Report",
            styles["Title"],
        )
    )

    elements.append(
        Spacer(
            1,
            0.2 * inch,
        )
    )

    # Project information
    elements.append(
        Paragraph(
            f"<b>Project:</b> {project.name}",
            styles["Normal"],
        )
    )

    elements.append(
        Paragraph(
            f"<b>Solution:</b> {solution.title}",
            styles["Normal"],
        )
    )

    elements.append(
        Spacer(
            1,
            0.3 * inch,
        )
    )

    # Summary table
    summary_data = [
        [
            "Total Requirements",
            "Compliant",
            "Partial",
            "Non-Compliant",
            "Overall Score",
        ],
        [
            str(total_requirements),
            str(compliant_count),
            str(partial_count),
            str(non_compliant_count),
            f"{overall_score}%",
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            1.3 * inch,
            1 * inch,
            0.9 * inch,
            1.2 * inch,
            1 * inch,
        ],
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.darkblue,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
            ]
        )
    )

    elements.append(
        summary_table
    )

    elements.append(
        Spacer(
            1,
            0.4 * inch,
        )
    )

    # Detailed analysis heading
    elements.append(
        Paragraph(
            "Detailed Compliance Analysis",
            styles["Heading2"],
        )
    )

    elements.append(
        Spacer(
            1,
            0.2 * inch,
        )
    )

    # Requirement-wise analysis
    for index, result in enumerate(
        compliance_results,
        start=1,
    ):

        elements.append(
            Paragraph(
                f"<b>Requirement {index}</b>",
                styles["Heading3"],
            )
        )

        elements.append(
            Paragraph(
                (
                    "<b>Tender Requirement:</b> "
                    f"{result.requirement.requirement_text}"
                ),
                styles["Normal"],
            )
        )

        elements.append(
            Paragraph(
                (
                    "<b>Status:</b> "
                    f"{result.get_status_display()}"
                ),
                styles["Normal"],
            )
        )

        elements.append(
            Paragraph(
                (
                    "<b>Confidence Score:</b> "
                    f"{result.confidence_score}%"
                ),
                styles["Normal"],
            )
        )

        elements.append(
            Paragraph(
                (
                    "<b>Analysis:</b> "
                    f"{result.explanation}"
                ),
                styles["Normal"],
            )
        )

        elements.append(
            Spacer(
                1,
                0.25 * inch,
            )
        )

    # Build PDF
    doc.build(
        elements
    )

    return response

def analyze_improvement_suggestions(request, project_id):

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

    failed_results = ComplianceResult.objects.filter(
        project=project,
        solution=solution,
        status__in=[
            "partial",
            "non_compliant",
        ],
    ).select_related(
        "requirement"
    )

    if not failed_results.exists():

        print(
            "NO REQUIREMENTS NEED IMPROVEMENT."
        )

        return redirect(
            "project_solution",
            project_id=project.id,
        )

    expected_requirement_ids = set(
        failed_results.values_list(
            "requirement_id",
            flat=True,
        )
    )

    analysis_result = None


    # TRY GEMINI AI

    try:

        analysis_result = (
            generate_improvement_suggestions(
                failed_results,
                solution.description,
            )
        )

        suggestions = analysis_result.get(
            "suggestions",
            [],
        )

        received_requirement_ids = set(
            item.get("requirement_id")
            for item in suggestions
            if item.get("requirement_id") is not None
        )

        is_valid_response = (

            isinstance(
                suggestions,
                list,
            )

            and len(suggestions)
            == len(expected_requirement_ids)

            and received_requirement_ids
            == expected_requirement_ids

            and len(received_requirement_ids)
            == len(suggestions)
        )

        if not is_valid_response:

            raise Exception(
                "Gemini returned incomplete or invalid "
                "improvement suggestions."
            )

        print(
            "GEMINI IMPROVEMENT ANALYSIS SUCCESSFUL"
        )


    # USE FALLBACK IF GEMINI FAILS

    except Exception as error:

        print(
            "AI IMPROVEMENT ANALYSIS FAILED."
        )

        print(
            "USING FALLBACK IMPROVEMENT SYSTEM:",
            error,
        )

        try:

            analysis_result = (
                generate_improvement_suggestions_fallback(
                    failed_results,
                    solution.description,
                )
            )

            print(
                "FALLBACK IMPROVEMENT ANALYSIS SUCCESSFUL"
            )

        except Exception as fallback_error:

            print(
                "FALLBACK IMPROVEMENT ERROR:",
                fallback_error,
            )

            return redirect(
                "project_solution",
                project_id=project.id,
            )


    suggestions = analysis_result.get(
        "suggestions",
        [],
    )

    # FINAL VALIDATION

    if not suggestions:

        print(
            "NO IMPROVEMENT SUGGESTIONS GENERATED."
        )

        return redirect(
            "project_solution",
            project_id=project.id,
        )


    # ONLY DELETE OLD SUGGESTIONS AFTER
    # NEW VALID SUGGESTIONS ARE AVAILABLE

    ImprovementSuggestion.objects.filter(
        project=project,
        solution=solution,
    ).delete()


    # SAVE NEW SUGGESTIONS

    valid_requirement_ids = expected_requirement_ids

    saved_count = 0

    for item in suggestions:

        requirement_id = item.get(
            "requirement_id"
        )

        if requirement_id not in valid_requirement_ids:

            print(
                f"INVALID REQUIREMENT ID: "
                f"{requirement_id}"
            )

            continue

        try:

            requirement = Requirement.objects.get(
                id=requirement_id,
            )

        except Requirement.DoesNotExist:

            continue


        suggestion_text = item.get(
            "suggestion",
            "",
        ).strip()

        priority = item.get(
            "priority",
            "medium",
        )


        # SKIP EMPTY SUGGESTIONS

        if not suggestion_text:

            continue


        # VALIDATE PRIORITY

        if priority not in [
            "high",
            "medium",
            "low",
        ]:

            priority = "medium"


        ImprovementSuggestion.objects.create(

            project=project,

            solution=solution,

            requirement=requirement,

            suggestion=suggestion_text,

            priority=priority,

        )

        saved_count += 1


    print(
        f"IMPROVEMENT SUGGESTIONS SAVED: "
        f"{saved_count}"
    )


    return redirect(
        "project_solution",
        project_id=project.id,
    )
    
def requirement_list(request, project_id):

    project = get_object_or_404(
        Project,
        id=project_id,
    )

    document = get_object_or_404(
        TenderDocument,
        project=project,
    )

    requirements = Requirement.objects.filter(
        document=document
    ).order_by(
        "id"
    )

    return render(
        request,
        "documents/requirement_list.html",
        {
            "project": project,
            "document": document,
            "requirements": requirements,
        },
    )


def requirement_create(request, project_id):

    project = get_object_or_404(
        Project,
        id=project_id,
    )

    document = get_object_or_404(
        TenderDocument,
        project=project,
    )

    if request.method == "POST":

        form = RequirementForm(
            request.POST,
        )

        if form.is_valid():

            requirement = form.save(
                commit=False,
            )

            requirement.document = document

            requirement.save()

            return redirect(
                "requirement_list",
                project_id=project.id,
            )

    else:

        form = RequirementForm()

    return render(
        request,
        "documents/requirement_form.html",
        {
            "project": project,
            "form": form,
            "page_title": "Add Requirement",
        },
    )


def requirement_edit(request, requirement_id):

    requirement = get_object_or_404(
        Requirement,
        id=requirement_id,
    )

    project = requirement.document.project

    if request.method == "POST":

        form = RequirementForm(
            request.POST,
            instance=requirement,
        )

        if form.is_valid():

            form.save()

            return redirect(
                "requirement_list",
                project_id=project.id,
            )

    else:

        form = RequirementForm(
            instance=requirement,
        )

    return render(
        request,
        "documents/requirement_form.html",
        {
            "project": project,
            "form": form,
            "requirement": requirement,
            "page_title": "Edit Requirement",
        },
    )


def requirement_delete(request, requirement_id):

    requirement = get_object_or_404(
        Requirement,
        id=requirement_id,
    )

    project_id = requirement.document.project.id

    if request.method == "POST":

        requirement.delete()

        return redirect(
            "requirement_list",
            project_id=project_id,
        )

    return render(
        request,
        "documents/requirement_confirm_delete.html",
        {
            "requirement": requirement,
        },
    )
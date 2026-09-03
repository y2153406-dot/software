def generate_improvement_suggestions_fallback(
    failed_results,
    solution_text,
):

    suggestions = []

    for result in failed_results:

        requirement_text = (
            result.requirement.requirement_text
        )

        status = result.status

        if status == "non_compliant":

            priority = "high"

            suggestion = (
                "The current project solution does not adequately "
                "address this tender requirement. Add a dedicated "
                "feature, module, process, or implementation approach "
                f"to satisfy the requirement: {requirement_text}"
            )

        else:

            priority = "medium"

            suggestion = (
                "The current project solution partially addresses "
                "this requirement. Strengthen the existing approach "
                "by adding clearer implementation details, relevant "
                "features, and specific functionality related to: "
                f"{requirement_text}"
            )

        suggestions.append(
            {
                "requirement_id": (
                    result.requirement.id
                ),
                "suggestion": suggestion,
                "priority": priority,
            }
        )

    return {
        "suggestions": suggestions
    }
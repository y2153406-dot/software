def analyze_risks_fallback(
    requirements,
    solution_text,
):

    results = []

    solution_text = (
        solution_text or ""
    ).lower()

    for requirement in requirements:

        requirement_text = (
            requirement.requirement_text or ""
        )

        requirement_lower = (
            requirement_text.lower()
        )

        matched_words = 0

        requirement_words = [
            word
            for word in requirement_lower.split()
            if len(word) > 3
        ]

        for word in requirement_words:

            if word in solution_text:

                matched_words += 1

        total_words = len(
            requirement_words
        )

        match_percentage = 0

        if total_words > 0:

            match_percentage = (
                matched_words / total_words
            ) * 100

        # Determine risk level

        if match_percentage >= 70:

            risk_level = "low"

            risk_score = 20

            explanation = (
                "The project solution appears to "
                "address most aspects of this requirement."
            )

            recommendation = (
                "Continue validating this requirement "
                "during implementation and testing."
            )

        elif match_percentage >= 35:

            risk_level = "medium"

            risk_score = 50

            explanation = (
                "The project solution partially addresses "
                "this requirement, but some details may "
                "still be missing."
            )

            recommendation = (
                "Add clearer implementation details and "
                "ensure all parts of the requirement "
                "are covered."
            )

        else:

            risk_level = "high"

            risk_score = 85

            explanation = (
                "The project solution does not clearly "
                "address this requirement."
            )

            recommendation = (
                "Update the project solution and implementation "
                "plan to explicitly address this requirement."
            )

        # Mandatory requirements increase risk

        if (
            requirement.is_mandatory
            and risk_level == "medium"
        ):

            risk_level = "high"

            risk_score = 75

            explanation = (
                "This is a mandatory requirement and "
                "the project solution does not fully "
                "address it."
            )

            recommendation = (
                "Prioritize this mandatory requirement "
                "and clearly include it in the project "
                "implementation plan."
            )

        results.append(
            {
                "requirement_id": requirement.id,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "explanation": explanation,
                "recommendation": recommendation,
            }
        )

    return {
        "results": results
    }
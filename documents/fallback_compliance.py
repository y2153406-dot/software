import re


STOP_WORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "for",
    "with",
    "from",
    "that",
    "this",
    "must",
    "should",
    "shall",
    "will",
    "be",
    "to",
    "of",
    "in",
    "on",
    "by",
    "is",
    "are",
    "as",
    "it",
}


def get_keywords(text):

    words = re.findall(
        r"\b[a-zA-Z]{4,}\b",
        text.lower(),
    )

    keywords = []

    for word in words:

        if word not in STOP_WORDS:

            keywords.append(
                word
            )

    return set(keywords)


def analyze_requirement_fallback(
    requirement_text,
    solution_text,
):

    requirement_keywords = get_keywords(
        requirement_text
    )

    solution_keywords = get_keywords(
        solution_text
    )

    if not requirement_keywords:

        return {
            "status": "partial",
            "confidence_score": 50,
            "explanation": (
                "The fallback system could not "
                "identify enough keywords for "
                "a detailed comparison."
            ),
        }

    matching_keywords = (
        requirement_keywords
        & solution_keywords
    )

    match_count = len(
        matching_keywords
    )

    total_keywords = len(
        requirement_keywords
    )

    match_percentage = (
        match_count / total_keywords
    ) * 100

    if match_percentage >= 50:

        status = "compliant"

        confidence_score = min(
            90,
            round(
                60 + match_percentage
            ),
        )

        explanation = (
            "The solution addresses several "
            "important concepts from this "
            "requirement."
        )

    elif match_percentage >= 20:

        status = "partial"

        confidence_score = min(
            75,
            round(
                40 + match_percentage
            ),
        )

        explanation = (
            "The solution partially addresses "
            "this requirement, but some "
            "important aspects may be missing."
        )

    else:

        status = "non_compliant"

        confidence_score = min(
            70,
            round(
                30 + match_percentage
            ),
        )

        explanation = (
            "The solution does not contain "
            "enough relevant information to "
            "confirm compliance with this "
            "requirement."
        )

    return {
        "status": status,
        "confidence_score": confidence_score,
        "explanation": explanation,
    }


def analyze_compliance_fallback(
    requirements,
    solution_text,
):

    results = []

    for requirement in requirements:

        analysis = (
            analyze_requirement_fallback(
                requirement.requirement_text,
                solution_text,
            )
        )

        results.append(
            {
                "requirement_id": requirement.id,
                "status": analysis["status"],
                "confidence_score": (
                    analysis[
                        "confidence_score"
                    ]
                ),
                "explanation": (
                    analysis[
                        "explanation"
                    ]
                ),
            }
        )

    return {
        "results": results
    }
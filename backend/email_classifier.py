import re


# =========================================================
# EMAIL RESPONSE CLASSIFIER
# =========================================================

def normalize_text(text):
    """
    Convert email text into a clean lowercase string.
    """

    if not text:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# KEYWORDS
# =========================================================

RESPONSE_KEYWORDS = {

    "Interview": [
        "interview invitation",
        "interview invite",
        "invite you to interview",
        "schedule an interview",
        "scheduled interview",
        "interview round",
        "technical interview",
        "interview process",
        "interview",
    ],

    "Assessment": [
        "online assessment",
        "coding assessment",
        "technical assessment",
        "assessment link",
        "assessment invitation",
        "take the assessment",
        "complete the assessment",
        "coding test",
        "technical test",
    ],

    "Rejected": [
        "regret to inform",
        "regret to let you know",
        "not moving forward",
        "will not be moving forward",
        "application was unsuccessful",
        "application has been unsuccessful",
        "not selected",
        "we have decided not to proceed",
        "position has been filled",
        "rejected",
    ],

    "Offer": [
        "job offer",
        "offer letter",
        "offer of employment",
        "pleased to offer",
        "we are delighted to offer",
        "employment offer",
        "congratulations on your offer",
    ],

    "Under Review": [
        "application is under review",
        "application under review",
        "currently reviewing your application",
        "reviewing your application",
        "your application is being reviewed",
        "application is being considered",
        "under consideration",
    ],

    "Application Received": [
        "application received",
        "we received your application",
        "thank you for applying",
        "thank you for your application",
        "application has been received",
        "successfully submitted",
        "application submitted",
    ],
}


# =========================================================
# CLASSIFY EMAIL
# =========================================================

def classify_email(subject, body):

    subject = normalize_text(subject)
    body = normalize_text(body)

    combined_text = (
        subject
        + " "
        + body
    )

    scores = {}

    # -----------------------------------------------------
    # CHECK EACH RESPONSE TYPE
    # -----------------------------------------------------

    for response_type, keywords in RESPONSE_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword in combined_text:

                # Subject matches are stronger
                if keyword in subject:
                    score += 3

                else:
                    score += 1

        scores[response_type] = score

    # -----------------------------------------------------
    # FIND BEST MATCH
    # -----------------------------------------------------

    best_response = max(
        scores,
        key=scores.get
    )

    best_score = scores[best_response]

    # -----------------------------------------------------
    # NO MATCH
    # -----------------------------------------------------

    if best_score == 0:

        return {
            "response_type": "Other",
            "confidence": 0,
            "message": "No known response type detected"
        }

    # -----------------------------------------------------
    # CONFIDENCE
    # -----------------------------------------------------

    if best_score >= 6:
        confidence = 95

    elif best_score >= 4:
        confidence = 90

    elif best_score >= 2:
        confidence = 80

    else:
        confidence = 70

    return {
        "response_type": best_response,
        "confidence": confidence,
        "message": (
            f"Detected email response: "
            f"{best_response}"
        )
    }

SYSTEM_ROLE = (
    "You are a senior corporate communication specialist with 15 years of experience "
    "drafting executive-level emails. You produce professional, well-structured emails "
    "that are clear, concise, and perfectly adapted to the requested tone."
)

FORMAT_INSTRUCTIONS = """Write the email using this exact structure:
1. Subject: (one concise line)
2. Greeting
3. Body (2-3 focused paragraphs)
4. Closing with sign-off

Rules:
- Seamlessly incorporate every listed fact into the email body.
- Never fabricate details that were not provided.
- Match the requested tone in word choice, sentence length, and formality level.
- Aim for under 180 words in the body to keep the message focused."""

FEW_SHOT_EXAMPLE_1_INPUT = (
    "Intent: Reschedule a project kickoff meeting\n"
    "Tone: formal\n"
    "Facts:\n"
    "- The meeting was originally set for Tuesday at 10 AM\n"
    "- Two engineering leads have a conflicting client workshop\n"
    "- Proposed new time is Wednesday at 2 PM\n"
    "- Attendees should confirm availability by end of day"
)

FEW_SHOT_EXAMPLE_1_OUTPUT = (
    "Subject: Request to Reschedule Project Kickoff Meeting\n\n"
    "Hello Team,\n\n"
    "I am writing to request a change to our project kickoff meeting, originally "
    "scheduled for Tuesday at 10 AM. Two of our engineering leads have a conflicting "
    "client workshop at that time and will be unable to attend.\n\n"
    "To ensure all key stakeholders are present, I propose we move the meeting to "
    "Wednesday at 2 PM. Please confirm your availability by end of day so we can "
    "lock in the new schedule.\n\n"
    "Best regards,\n[Your Name]"
)

FEW_SHOT_EXAMPLE_2_INPUT = (
    "Intent: Thank a client after a quarterly business review\n"
    "Tone: empathetic\n"
    "Facts:\n"
    "- The client gave candid feedback during the review\n"
    "- They experienced delivery delays in March\n"
    "- A revised timeline will be shared by Friday\n"
    "- The team is committed to improving response times"
)

FEW_SHOT_EXAMPLE_2_OUTPUT = (
    "Subject: Thank You for Your Feedback During the Quarterly Review\n\n"
    "Dear [Client Name],\n\n"
    "Thank you for the candid feedback you shared during our quarterly review. "
    "We genuinely appreciate your openness in highlighting where the experience "
    "fell short of expectations.\n\n"
    "I want to acknowledge the delivery delays your team experienced in March. "
    "We understand the impact on your planning, and improving our response times "
    "is a top priority. We will share a revised implementation timeline with you "
    "by Friday.\n\n"
    "Warm regards,\n[Your Name]"
)


def build_prompt(intent, facts, tone, use_few_shot=True):
    """Assemble the full prompt string for the Gemini API."""
    facts_block = "\n".join(f"- {f}" for f in facts)

    parts = [f"{SYSTEM_ROLE}\n\n{FORMAT_INSTRUCTIONS}\n"]

    if use_few_shot:
        parts.append("--- Example 1 ---")
        parts.append(f"Input:\n{FEW_SHOT_EXAMPLE_1_INPUT}")
        parts.append(f"Output:\n{FEW_SHOT_EXAMPLE_1_OUTPUT}")
        parts.append("--- Example 2 ---")
        parts.append(f"Input:\n{FEW_SHOT_EXAMPLE_2_INPUT}")
        parts.append(f"Output:\n{FEW_SHOT_EXAMPLE_2_OUTPUT}")
        parts.append("--- Now generate ---\n")

    parts.append(
        f"Intent: {intent}\n"
        f"Tone: {tone}\n"
        f"Facts:\n{facts_block}\n\n"
        "Generate the email now."
    )

    return "\n\n".join(parts)

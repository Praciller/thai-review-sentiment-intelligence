from scripts.check_repo_guardrails import find_text_violations


def test_guardrails_report_marker_names_without_exposing_values():
    findings = find_text_violations(
        {
            "data/private.csv": "email,review\nname@example.com,private text",
            "README.md": "This is a production-ready " + "sentiment model.",
            ".env.example": "API_KEY=replace-with-your-key",
        }
    )

    assert findings == [
        "README.md: unsupported-claim",
        "data/private.csv: email-like-data",
    ]

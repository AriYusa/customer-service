"""Technical support utilities."""

from __future__ import annotations

import uuid
from datetime import datetime

from customer_service.datamodels.support import (
    BugReportResult,
    CallbackResult,
    FeatureRequestResult,
    MaintenanceWindow,
    ServiceStatus,
    SupportTicketResult,
    SystemStatus,
    TicketCloseResult,
    TicketStatus,
    TicketUpdateResult,
    TroubleshootingGuide,
    TroubleshootStep,
)


def create_support_ticket(
    customer_id: str, issue_type: str, description: str, priority: str = "medium"
) -> SupportTicketResult:
    """Create a technical support ticket.

    Args:
        customer_id: The ID of the customer account
        issue_type: Type of issue (login, website, mobile_app, payment, product_defect, other)
        description: Detailed description of the issue
        priority: Priority level (low, medium, high, urgent) - default: medium

    Returns:
        SupportTicketResult with ticket details
    """
    ticket_id = f"ticket-{uuid.uuid4()}"

    return SupportTicketResult(
        success=True,
        ticket_id=ticket_id,
        status="open",
        assigned_to="Technical Support Team",
        created_date=datetime.now().isoformat(),
        expected_response="Within 24 hours"
        if priority in ["high", "urgent"]
        else "Within 48 hours",
    )


def get_troubleshooting_steps(issue_type: str) -> TroubleshootingGuide:
    """Get troubleshooting steps for common technical issues.

    Args:
        issue_type: Type of issue (login, website_error, mobile_app_crash, payment_failed, slow_performance, other)

    Returns:
        TroubleshootingGuide with troubleshooting information
    """
    troubleshooting_guides = {
        "login": {
            "steps": [
                TroubleshootStep(
                    step_number=1,
                    instruction="Verify you're using the correct email address",
                    estimated_time="1 minute",
                ),
                TroubleshootStep(
                    step_number=2,
                    instruction="Click 'Forgot Password' to reset your password",
                    estimated_time="2 minutes",
                ),
                TroubleshootStep(
                    step_number=3,
                    instruction="Clear your browser cache and cookies",
                    estimated_time="2 minutes",
                ),
                TroubleshootStep(
                    step_number=4,
                    instruction="Try logging in from a different browser or device",
                    estimated_time="3 minutes",
                ),
                TroubleshootStep(
                    step_number=5,
                    instruction="Check if Caps Lock is on",
                    estimated_time="1 minute",
                ),
                TroubleshootStep(
                    step_number=6,
                    instruction="Disable any browser extensions that might interfere",
                    estimated_time="3 minutes",
                ),
            ],
            "estimated_time": "10-15 minutes",
            "additional_resources": [
                "https://example.com/help/login-issues",
                "https://example.com/help/password-reset",
            ],
        },
        "website_error": {
            "steps": [
                TroubleshootStep(
                    step_number=1,
                    instruction="Refresh the page (Ctrl+R or Cmd+R)",
                    estimated_time="1 minute",
                ),
                TroubleshootStep(
                    step_number=2,
                    instruction="Clear your browser cache and cookies",
                    estimated_time="2 minutes",
                ),
                TroubleshootStep(
                    step_number=3,
                    instruction="Try a different browser (Chrome, Firefox, Safari, Edge)",
                    estimated_time="2 minutes",
                ),
                TroubleshootStep(
                    step_number=4,
                    instruction="Disable browser extensions temporarily",
                    estimated_time="2 minutes",
                ),
                TroubleshootStep(
                    step_number=5,
                    instruction="Check your internet connection",
                    estimated_time="1 minute",
                ),
                TroubleshootStep(
                    step_number=6,
                    instruction="Try accessing the site in incognito/private mode",
                    estimated_time="2 minutes",
                ),
            ],
            "estimated_time": "10 minutes",
            "additional_resources": [
                "https://example.com/help/website-troubleshooting",
                "https://example.com/help/browser-compatibility",
            ],
        },
        "mobile_app_crash": {
            "steps": [
                TroubleshootStep(
                    step_number=1,
                    instruction="Force close the app completely",
                    estimated_time="1 minute",
                ),
                TroubleshootStep(
                    step_number=2,
                    instruction="Restart your device",
                    estimated_time="3 minutes",
                ),
                TroubleshootStep(
                    step_number=3,
                    instruction="Check for app updates in the App Store/Play Store",
                    estimated_time="2 minutes",
                ),
                TroubleshootStep(
                    step_number=4,
                    instruction="Ensure you have enough storage space on your device",
                    estimated_time="2 minutes",
                ),
                TroubleshootStep(
                    step_number=5,
                    instruction="Clear app cache in device settings",
                    estimated_time="3 minutes",
                ),
                TroubleshootStep(
                    step_number=6,
                    instruction="Uninstall and reinstall the app (as a last resort)",
                    estimated_time="5 minutes",
                ),
            ],
            "estimated_time": "15-20 minutes",
            "additional_resources": [
                "https://example.com/help/mobile-app-troubleshooting",
                "https://example.com/help/app-updates",
            ],
        },
        "payment_failed": {
            "steps": [
                TroubleshootStep(
                    step_number=1,
                    instruction="Verify your payment information is correct",
                    estimated_time="2 minutes",
                ),
                TroubleshootStep(
                    step_number=2,
                    instruction="Check that your card has not expired",
                    estimated_time="1 minute",
                ),
                TroubleshootStep(
                    step_number=3,
                    instruction="Ensure you have sufficient funds available",
                    estimated_time="2 minutes",
                ),
                TroubleshootStep(
                    step_number=4,
                    instruction="Contact your bank to ensure they're not blocking the transaction",
                    estimated_time="5 minutes",
                ),
                TroubleshootStep(
                    step_number=5,
                    instruction="Try a different payment method",
                    estimated_time="2 minutes",
                ),
                TroubleshootStep(
                    step_number=6,
                    instruction="Check if your billing address matches your card",
                    estimated_time="2 minutes",
                ),
            ],
            "estimated_time": "10 minutes",
            "additional_resources": [
                "https://example.com/help/payment-issues",
                "https://example.com/help/accepted-payment-methods",
            ],
        },
        "slow_performance": {
            "steps": [
                TroubleshootStep(
                    step_number=1,
                    instruction="Check your internet connection speed",
                    estimated_time="2 minutes",
                ),
                TroubleshootStep(
                    step_number=2,
                    instruction="Close unnecessary browser tabs and applications",
                    estimated_time="2 minutes",
                ),
                TroubleshootStep(
                    step_number=3,
                    instruction="Clear browser cache and cookies",
                    estimated_time="2 minutes",
                ),
                TroubleshootStep(
                    step_number=4,
                    instruction="Restart your device",
                    estimated_time="3 minutes",
                ),
                TroubleshootStep(
                    step_number=5,
                    instruction="Try using a wired connection instead of WiFi",
                    estimated_time="3 minutes",
                ),
                TroubleshootStep(
                    step_number=6,
                    instruction="Disable VPN if you're using one",
                    estimated_time="2 minutes",
                ),
            ],
            "estimated_time": "15 minutes",
            "additional_resources": [
                "https://example.com/help/performance-optimization"
            ],
        },
    }

    guide = troubleshooting_guides.get(
        issue_type,
        {
            "steps": [
                TroubleshootStep(
                    step_number=1,
                    instruction="Document the specific issue and any error messages",
                    estimated_time="3 minutes",
                ),
                TroubleshootStep(
                    step_number=2,
                    instruction="Note when the issue started occurring",
                    estimated_time="2 minutes",
                ),
                TroubleshootStep(
                    step_number=3,
                    instruction="Try restarting the affected device or application",
                    estimated_time="3 minutes",
                ),
                TroubleshootStep(
                    step_number=4,
                    instruction="Contact support for personalized assistance",
                    estimated_time="5 minutes",
                ),
            ],
            "estimated_time": "Varies",
            "additional_resources": ["https://example.com/help/general-support"],
        },
    )

    return TroubleshootingGuide(
        issue_type=issue_type,
        steps=guide["steps"],
        estimated_time=guide.get("estimated_time", "Varies"),
        additional_resources=guide.get("additional_resources", []),
        escalation_available=True,
    )


def check_system_status() -> SystemStatus:
    """Check the current status of system services and known issues.

    Returns:
        SystemStatus with system health information
    """
    return SystemStatus(
        overall_status="operational",
        services=[
            ServiceStatus(name="Website", status="operational", uptime="99.9%"),
            ServiceStatus(name="Mobile App", status="operational", uptime="99.8%"),
            ServiceStatus(
                name="Payment Processing", status="operational", uptime="100%"
            ),
            ServiceStatus(
                name="Order Management", status="operational", uptime="99.7%"
            ),
            ServiceStatus(name="Customer Portal", status="operational", uptime="99.9%"),
        ],
        known_issues=[],
        scheduled_maintenance=[
            MaintenanceWindow(
                service="Website",
                start="2025-10-28 02:00 AM EST",
                end="2025-10-28 04:00 AM EST",
                description="Routine database maintenance",
            )
        ],
        last_updated=datetime.now().isoformat(),
    )


def report_bug(
    customer_id: str,
    description: str,
    steps_to_reproduce: list[str],
    attachments: list[str],
    severity: str = "medium",
) -> BugReportResult:
    """Report a software bug or technical issue.

    Args:
        customer_id: The ID of the customer account
        description: Detailed description of the bug
        steps_to_reproduce: List of steps to reproduce the issue
        severity: Bug severity (low, medium, high, critical) - default: medium
        attachments: Optional list of screenshot URLs or file references

    Returns:
        BugReportResult with bug report details
    """
    bug_id = f"bug-{uuid.uuid4()}"

    return BugReportResult(
        success=True,
        bug_id=bug_id,
        status="submitted",
        acknowledgment="Thank you for reporting this issue. Our team will investigate.",
        tracking_url=f"https://example.com/bugs/{bug_id}",
    )


def request_feature(
    customer_id: str, feature_description: str, use_case: str
) -> FeatureRequestResult:
    """Submit a feature request or enhancement suggestion.

    Args:
        customer_id: The ID of the customer account
        feature_description: Detailed description of the requested feature
        use_case: Explanation of how this feature would be used/beneficial

    Returns:
        FeatureRequestResult with feature request details
    """
    request_id = f"feature-{uuid.uuid4()}"

    return FeatureRequestResult(
        success=True,
        request_id=request_id,
        status="submitted",
        acknowledgment="Thank you for your suggestion! We'll review it with our product team.",
        voting_url=f"https://example.com/features/{request_id}/vote",
    )


def get_ticket_status(ticket_id: str) -> TicketStatus:
    """Get the current status and details of a support ticket.

    Args:
        ticket_id: The unique ticket identifier

    Returns:
        TicketStatus with ticket information
    """
    # Mock ticket status
    return TicketStatus(
        ticket_id=ticket_id,
        status="in_progress",
        priority="medium",
        subject="Technical issue with checkout process",
        created_date="2025-10-24T10:30:00",
        last_updated="2025-10-25T14:22:00",
        assigned_to="Sarah from Technical Support",
        responses=2,
        resolution="",
    )


def update_ticket(
    ticket_id: str, message: str, attachments: list[str] | None = None
) -> TicketUpdateResult:
    """Add an update or response to an existing support ticket.

    Args:
        ticket_id: The unique ticket identifier
        message: Additional information or response to add
        attachments: Optional list of file URLs or references

    Returns:
        TicketUpdateResult with update confirmation
    """
    return TicketUpdateResult(
        success=True,
        message="Your update has been added to the ticket. A support agent will respond shortly.",
        updated_at=datetime.now().isoformat(),
    )


def close_ticket(
    ticket_id: str, satisfaction_rating: int | None = None, feedback: str | None = None
) -> TicketCloseResult:
    """Close a resolved support ticket.

    Args:
        ticket_id: The unique ticket identifier
        satisfaction_rating: Optional satisfaction rating (1-5)
        feedback: Optional feedback about the support experience

    Returns:
        TicketCloseResult with closure confirmation
    """
    return TicketCloseResult(
        success=True,
        message="Ticket closed successfully. Thank you for your feedback!",
        closed_at=datetime.now().isoformat(),
    )


def request_callback(
    customer_id: str, phone_number: str, preferred_time: str, issue_summary: str
) -> CallbackResult:
    """Request a callback from technical support.

    Args:
        customer_id: The ID of the customer account
        phone_number: Phone number for the callback
        preferred_time: Preferred time for callback (e.g., "2025-10-26 14:00")
        issue_summary: Brief summary of the issue

    Returns:
        CallbackResult with callback confirmation
    """
    callback_id = f"callback-{uuid.uuid4()}"

    return CallbackResult(
        success=True,
        callback_id=callback_id,
        scheduled_time=preferred_time,
        confirmation_message=f"A technical support specialist will call you at {phone_number} on {preferred_time}",
    )

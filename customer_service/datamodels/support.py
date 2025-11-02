"""Technical support data models."""

from __future__ import annotations

from pydantic import BaseModel


class SupportTicketResult(BaseModel):
    """Support ticket creation result."""

    success: bool
    ticket_id: str
    status: str
    assigned_to: str
    created_date: str
    expected_response: str


class TroubleshootStep(BaseModel):
    """Individual troubleshooting step."""

    step_number: int
    instruction: str
    estimated_time: str


class TroubleshootingGuide(BaseModel):
    """Troubleshooting guide for an issue."""

    issue_type: str
    steps: list[TroubleshootStep]
    estimated_time: str
    additional_resources: list[str]
    escalation_available: bool


class ServiceStatus(BaseModel):
    """Individual service status."""

    name: str
    status: str
    uptime: str


class MaintenanceWindow(BaseModel):
    """Scheduled maintenance information."""

    service: str
    start: str
    end: str
    description: str


class SystemStatus(BaseModel):
    """Overall system status."""

    overall_status: str
    services: list[ServiceStatus]
    known_issues: list[str]
    scheduled_maintenance: list[MaintenanceWindow]
    last_updated: str


class BugReportResult(BaseModel):
    """Bug report submission result."""

    success: bool
    bug_id: str
    status: str
    acknowledgment: str
    tracking_url: str


class FeatureRequestResult(BaseModel):
    """Feature request submission result."""

    success: bool
    request_id: str
    status: str
    acknowledgment: str
    voting_url: str


class TicketStatus(BaseModel):
    """Support ticket status."""

    ticket_id: str
    status: str
    priority: str
    subject: str
    created_date: str
    last_updated: str
    assigned_to: str
    responses: int
    resolution: str


class TicketUpdateResult(BaseModel):
    """Ticket update result."""

    success: bool
    message: str
    updated_at: str


class TicketCloseResult(BaseModel):
    """Ticket close result."""

    success: bool
    message: str
    closed_at: str


class CallbackResult(BaseModel):
    """Callback request result."""

    success: bool
    callback_id: str
    scheduled_time: str
    confirmation_message: str

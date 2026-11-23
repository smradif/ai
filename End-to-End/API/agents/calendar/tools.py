from langchain.tools import tool


@tool
def create_calendar_event(
    title: str, start_time: str, end_time: str, attendees: list[str], location: str = ""
) -> str:
    """Create calendar events. Start time and end time must be inISO format"""
    return f"Event created: {title} from {start_time} to {end_time} with {len(attendees)} attendees"


@tool
def send_email(subject: str, to: list[str], body: str, cc: list[str] = []) -> str:
    """Send an email via email API. Requires properly formatted addresses"""
    return f"Email sent to {' '.join(to)} - Subject: {subject}"


@tool
def get_available_time_slots(date: str, duration_minutes: int, attendees: list[str]):
    """Check calendar availability for given attendees on a specific date."""
    return ["09:00", "14:00", "16:00"]

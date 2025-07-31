from enum import Enum

class ClassStatus(Enum):
    """Enum for class status."""
    ACTIVE = "active"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled" 
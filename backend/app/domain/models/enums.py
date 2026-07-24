from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class HealthLiteracyLevel(str, Enum):
    """Niveau de compréhension médicale du patient.
    Utilisé par l'Agent Personnalisateur pour adapter le langage."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Severity(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class TreatmentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
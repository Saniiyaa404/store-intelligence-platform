from pydantic import BaseModel
from typing import Optional
from typing import Dict
from typing import Any


class Event(BaseModel):

    event_id: str
    store_id: str
    camera_id: str

    visitor_id: Optional[str]

    event_type: str
    timestamp: str

    zone_id: Optional[str]

    dwell_ms: int

    is_staff: bool

    confidence: float

    metadata: Dict[str, Any]
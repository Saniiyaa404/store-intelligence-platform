from fastapi import FastAPI

from app.models import Event
from app.ingestion import ingest_events
from app.metrics import calculate_metrics
from app.funnel import calculate_funnel
from app.heatmap import calculate_heatmap
from app.anomalies import detect_anomalies
from app.health import get_health
from app import database


app = FastAPI(
    title="Store Intelligence API"
)


@app.get("/health")
def health():

    return get_health()


@app.post("/events/ingest")
def ingest(events: list[Event]):

    result = ingest_events(
        events
    )

    return result


@app.get("/stores/{store_id}/metrics")
def metrics(store_id: str):

    return calculate_metrics(
        store_id
    )


@app.get(
    "/stores/{store_id}/funnel"
)
def funnel(store_id: str):

    return calculate_funnel(
        store_id
    )


@app.get(
    "/stores/{store_id}/heatmap"
)
def heatmap(store_id):

    return calculate_heatmap(
        store_id
    )


@app.get(
    "/stores/{store_id}/anomalies"
)
def anomalies(store_id):

    return detect_anomalies(
        store_id
    )

#temporary -> remove before submission
from app.ingestion import clear_events

@app.post("/reset")
def reset():

    clear_events()

    return {
        "status": "cleared"
    }
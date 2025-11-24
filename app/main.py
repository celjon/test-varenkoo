from fastapi import FastAPI
from app.database import init_db
from app.api import operators, sources, contacts, leads

app = FastAPI(
    title="Mini-CRM API",
    description="Lead distribution system between operators based on sources",
    version="1.0.0"
)


@app.on_event("startup")
def startup_event():
    init_db()


app.include_router(operators.router)
app.include_router(sources.router)
app.include_router(contacts.router)
app.include_router(leads.router)


@app.get("/")
def root():
    return {
        "message": "Mini-CRM API",
        "version": "1.0.0",
        "docs": "/docs"
    }

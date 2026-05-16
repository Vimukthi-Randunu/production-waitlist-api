from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import waitlist, admin

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Waitlist API")

app.include_router(waitlist.router)
app.include_router(admin.router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
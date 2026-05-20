from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import waitlist, admin
import time
import sqlalchemy

def wait_for_db():
    max_retries = 10
    retry_interval = 3
    for attempt in range(max_retries):
        try:
            models.Base.metadata.create_all(bind=engine)
            print("Database connected successfully")
            return
        except sqlalchemy.exc.OperationalError:
            print(f"Database not ready, retrying in {retry_interval}s... (attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_interval)
    raise Exception("Could not connect to database after multiple retries")

wait_for_db()

app = FastAPI(title="Waitlist API")

app.include_router(waitlist.router)
app.include_router(admin.router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
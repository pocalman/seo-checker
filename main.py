from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl

from scraper import analyze_url
from database import SessionLocal, engine
from models import Base, Analysis

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# ------------------------
# MODEL INPUT
# ------------------------
class URLRequest(BaseModel):
    url: str   # 👈 IMPORTANT FIX (voir explication plus bas)


# ------------------------
# HOME
# ------------------------
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# ------------------------
# ANALYZE
# ------------------------
@app.post("/analyze")
async def analyze(data: URLRequest):

    result = await analyze_url(data.url)

    db = SessionLocal()

    try:
        analysis = Analysis(
            url=result["url"],
            seo_score=result["seo"]["score"],
            gseo_score=result["gseo"]["score"]
        )

        db.add(analysis)
        db.commit()

    finally:
        db.close()

    return result


# ------------------------
# HISTORY (API JSON)
# ------------------------
@app.get("/history")
def history():

    db = SessionLocal()

    try:
        rows = (
            db.query(Analysis)
            .order_by(Analysis.id.desc())
            .limit(50)
            .all()
        )

        return [
            {
                "id": r.id,
                "url": r.url,
                "seo_score": r.seo_score,
                "gseo_score": r.gseo_score
            }
            for r in rows
        ]

    finally:
        db.close()


# ------------------------
# DASHBOARD (OPTIONNEL JINJA)
# ------------------------
@app.get("/dashboard")
def dashboard(request: Request):

    db = SessionLocal()

    try:
        rows = (
            db.query(Analysis)
            .order_by(Analysis.id.desc())
            .limit(50)
            .all()
        )

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "rows": rows
            }
        )

    finally:
        db.close()
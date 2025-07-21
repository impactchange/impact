from fastapi import FastAPI
from core.config import setup_cors
from routers import auth, assessments, projects

app = FastAPI(title="IMPACT Methodology API", version="1.0.0")
setup_cors(app)

app.include_router(auth.router, prefix="/auth")
app.include_router(assessments.router, prefix="/assessments")
app.include_router(projects.router, prefix="/projects")

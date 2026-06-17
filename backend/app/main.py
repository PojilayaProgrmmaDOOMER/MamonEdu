from fastapi import FastAPI
from app.routes.topics import router as topics_router
from app.routes.auth import router as auth_router
from app.routes.materials import router as materials_router
from app.routes.tests import router as tests_router
from app.routes.ontology import router as ontology_router
from app.routes.practical import router as practical_router
#from app.routes.segmentation import router as segmentation_router
from app.routes.users import router as users_router
from app.routes.study_groups import router as study_groups_router
from app.routes.material_search import router as material_search_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
app = FastAPI(
    title="MamontEdu API",
    version="0.1.0"
)
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(material_search_router)
app.include_router(auth_router)
app.include_router(topics_router)
app.include_router(materials_router)
app.include_router(tests_router)
app.include_router(ontology_router)
app.include_router(practical_router)
#app.include_router(segmentation_router)
app.include_router(users_router)
app.include_router(study_groups_router)

@app.get("/")
def root():
    return {"message": "AI EduSeg backend works"}
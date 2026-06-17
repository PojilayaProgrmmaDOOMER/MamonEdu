from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.material import Material
from app.models.topic import Topic
from app.models.user import User
from app.models.material_concept import MaterialConcept
from app.models.ontology_concept import OntologyConcept
from app.schemas.material import MaterialConceptLinkCreate

from app.schemas.material import (
    MaterialCreate,
    MaterialUpdate,
    MaterialResponse
)

from app.auth.security import get_current_user, require_teacher_or_admin

router = APIRouter(
    prefix="/materials",
    tags=["Materials"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=MaterialResponse)
def create_material(
    material: MaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    topic = db.query(Topic).filter(
        Topic.id == material.topic_id
    ).first()

    if topic is None:
        raise HTTPException(
            status_code=404,
            detail="Topic not found"
        )

    new_material = Material(
        topic_id=material.topic_id,
        title=material.title,
        content=material.content,
        material_type=material.material_type,
        source_url=material.source_url
    )

    db.add(new_material)
    db.commit()
    db.refresh(new_material)

    return new_material


@router.get("/", response_model=list[MaterialResponse])
def get_materials(db: Session = Depends(get_db)):
    materials = db.query(Material).all()
    return materials


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(
    material_id: int,
    db: Session = Depends(get_db)
):
    material = db.query(Material).filter(
        Material.id == material_id
    ).first()

    if material is None:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    return material


@router.put("/{material_id}", response_model=MaterialResponse)
def update_material(
    material_id: int,
    material_data: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    material = db.query(Material).filter(
        Material.id == material_id
    ).first()

    if material is None:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    material.title = material_data.title
    material.content = material_data.content
    material.material_type = material_data.material_type
    material.source_url = material_data.source_url

    db.commit()
    db.refresh(material)

    return material


@router.delete("/{material_id}")
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    material = db.query(Material).filter(
        Material.id == material_id
    ).first()

    if material is None:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    db.delete(material)
    db.commit()

    return {
        "message": "Material deleted successfully"
    }

@router.post("/{material_id}/concepts")
def link_material_to_concept(
    material_id: int,
    data: MaterialConceptLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    material = db.query(Material).filter(Material.id == material_id).first()

    if material is None:
        raise HTTPException(status_code=404, detail="Material not found")

    concept = db.query(OntologyConcept).filter(
        OntologyConcept.id == data.concept_id
    ).first()

    if concept is None:
        raise HTTPException(status_code=404, detail="Concept not found")

    existing_link = db.query(MaterialConcept).filter(
        MaterialConcept.material_id == material_id,
        MaterialConcept.concept_id == data.concept_id,
    ).first()

    if existing_link is not None:
        raise HTTPException(
            status_code=400,
            detail="Material already linked to this concept"
        )

    link = MaterialConcept(
        material_id=material_id,
        concept_id=data.concept_id,
    )

    db.add(link)
    db.commit()

    return {"message": "Material linked to concept"}


@router.get("/{material_id}/concepts")
def get_material_concepts(
    material_id: int,
    db: Session = Depends(get_db),
):
    links = db.query(MaterialConcept).filter(
        MaterialConcept.material_id == material_id
    ).all()

    result = []

    for link in links:
        concept = db.query(OntologyConcept).filter(
            OntologyConcept.id == link.concept_id
        ).first()

        if concept is not None:
            result.append({
                "id": concept.id,
                "name": concept.name,
                "difficulty_level": concept.difficulty_level,
            })

    return result
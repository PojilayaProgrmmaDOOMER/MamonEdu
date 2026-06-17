from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import requests
from app.auth.security import require_teacher_or_admin
from app.database import SessionLocal
import feedparser
from urllib.parse import quote
from app.models.user import User
from app.models.material_search_profile import MaterialSearchProfile
from app.models.external_material_candidate import ExternalMaterialCandidate
from fastapi import HTTPException
from app.models.material import Material
from app.models.ontology_entity import OntologyEntity
from app.models.material_concept import MaterialConcept

from app.schemas.material_search import (
    MaterialSearchProfileCreate,
    MaterialSearchProfileResponse,
    ExternalMaterialCandidateResponse,
    ApproveMaterialCandidateRequest,
)


router = APIRouter(prefix="/material-search", tags=["Material Search"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/profiles", response_model=MaterialSearchProfileResponse)
def create_search_profile(
    profile: MaterialSearchProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    new_profile = MaterialSearchProfile(
        teacher_id=current_user.id,
        course_id=profile.course_id,
        name=profile.name,
        keywords=profile.keywords,
        source=profile.source,
        required_keywords=profile.required_keywords,
        excluded_keywords=profile.excluded_keywords,
        max_results=profile.max_results,
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


@router.get("/profiles", response_model=list[MaterialSearchProfileResponse])
def get_my_search_profiles(
    course_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    query = db.query(MaterialSearchProfile).filter(
        MaterialSearchProfile.teacher_id == current_user.id
    )

    if course_id is not None:
        query = query.filter(MaterialSearchProfile.course_id == course_id)

    return query.all()


@router.get("/candidates", response_model=list[ExternalMaterialCandidateResponse])
def get_material_candidates(
    course_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    profiles_query = db.query(MaterialSearchProfile).filter(
        MaterialSearchProfile.teacher_id == current_user.id
    )

    if course_id is not None:
        profiles_query = profiles_query.filter(
            MaterialSearchProfile.course_id == course_id
        )

    profiles = profiles_query.all()
    profile_ids = [profile.id for profile in profiles]

    if not profile_ids:
        return []

    return db.query(ExternalMaterialCandidate).filter(
        ExternalMaterialCandidate.search_profile_id.in_(profile_ids),
        ExternalMaterialCandidate.status == "pending",
    ).all()

@router.post("/profiles/{profile_id}/run")
def run_search_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    profile = db.query(MaterialSearchProfile).filter(
        MaterialSearchProfile.id == profile_id,
        MaterialSearchProfile.teacher_id == current_user.id,
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Search profile not found"
        )

    if profile.source != "arxiv":
        raise HTTPException(
            status_code=400,
            detail="Only arxiv source is supported now"
        )

    query = quote(profile.keywords)
    url = (
        "https://export.arxiv.org/api/query?"
        f"search_query=all:{query}"
        "&start=0"
        f"&max_results={profile.max_results}"
        "&sortBy=submittedDate"
        "&sortOrder=descending"
    )

    response = requests.get(url, verify=False, timeout=20)
    feed = feedparser.parse(response.text)
    print("ARXIV URL:", url)
    print("HTTP STATUS:", response.status_code)
    print("ENTRIES COUNT:", len(feed.entries))
    created_candidates = []

    

    required_keywords = []
    if profile.required_keywords:
        required_keywords = [
            word.strip().lower()
            for word in profile.required_keywords.split(",")
            if word.strip()
        ]

    excluded_keywords = []
    if profile.excluded_keywords:
        excluded_keywords = [
            word.strip().lower()
            for word in profile.excluded_keywords.split(",")
            if word.strip()
        ]
    for entry in feed.entries:
        title = entry.title.strip()
        abstract = entry.summary.strip()
        text_for_filter = f"{title} {abstract}".lower()

        if len(required_keywords) > 0:
            matched_required_count = sum(
                1 for keyword in required_keywords
                if keyword in text_for_filter
            )

            if matched_required_count < len(required_keywords):
                continue

        if len(excluded_keywords) > 0:
            if any(keyword in text_for_filter for keyword in excluded_keywords):
                continue
        source_url = entry.link

        authors = ", ".join(
            author.name for author in entry.authors
        ) if hasattr(entry, "authors") else None

        existing_candidate = db.query(ExternalMaterialCandidate).filter(
            ExternalMaterialCandidate.search_profile_id == profile.id,
            ExternalMaterialCandidate.source_url == source_url,
        ).first()

        if existing_candidate is not None:
            continue

        candidate = ExternalMaterialCandidate(
            search_profile_id=profile.id,
            title=title,
            authors=authors,
            abstract=abstract,
            source_url=source_url,
            source="arxiv",
            status="pending",
        )

        db.add(candidate)
        created_candidates.append(candidate)

    db.commit()

    return {
        "message": "Search completed",
        "created_candidates_count": len(created_candidates),
    }

def normalize_text(text: str) -> str:
    return (
        text.lower()
        .replace("-", " ")
        .replace("_", " ")
        .replace("/", " ")
        .replace("–", " ")
    )


def get_concept_aliases(concept_name: str) -> list[str]:
    name = normalize_text(concept_name)

    aliases = {name}

    if name == "u net":
        aliases.update(["unet", "u-net", "u net"])

    if name == "cnn":
        aliases.update(["cnn", "convolutional neural network", "convolutional neural networks"])

    if name == "iou":
        aliases.update(["iou", "intersection over union"])

    if name == "dice":
        aliases.update(["dice", "dice coefficient", "dice score"])

    if name == "deeplabv3":
        aliases.update(["deeplabv3", "deeplab v3", "deep lab v3"])

    if name == "semantic segmentation":
        aliases.update(["semantic segmentation"])

    if name == "instance segmentation":
        aliases.update(["instance segmentation"])

    if name == "convolution":
        aliases.update(["convolution", "convolutional", "convolutional operation"])

    return list(aliases)

@router.delete("/candidates")
def clear_material_candidates(
    course_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    profiles_query = db.query(MaterialSearchProfile).filter(
        MaterialSearchProfile.teacher_id == current_user.id
    )

    if course_id is not None and hasattr(MaterialSearchProfile, "course_id"):
        profiles_query = profiles_query.filter(
            MaterialSearchProfile.course_id == course_id
        )

    profile_ids = [profile.id for profile in profiles_query.all()]

    if not profile_ids:
        return {"message": "No candidates to clear"}

    db.query(ExternalMaterialCandidate).filter(
        ExternalMaterialCandidate.search_profile_id.in_(profile_ids),
        ExternalMaterialCandidate.status.in_(["pending", "rejected"]),
    ).delete(synchronize_session=False)

    db.commit()

    return {"message": "Material candidates cleared"}


@router.delete("/profiles/{profile_id}")
def delete_search_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    profile = db.query(MaterialSearchProfile).filter(
        MaterialSearchProfile.id == profile_id
    ).first()

    if profile is None:
        raise HTTPException(status_code=404, detail="Search profile not found")

    if current_user.role != "admin" and profile.teacher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can delete only your own profiles"
        )

    db.query(ExternalMaterialCandidate).filter(
        ExternalMaterialCandidate.search_profile_id == profile.id
    ).delete(synchronize_session=False)

    db.delete(profile)
    db.commit()

    return {"message": "Search profile deleted"}



@router.post("/candidates/{candidate_id}/approve")
def approve_material_candidate(
    candidate_id: int,
    data: ApproveMaterialCandidateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    candidate = db.query(ExternalMaterialCandidate).filter(
        ExternalMaterialCandidate.id == candidate_id
    ).first()

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    profile = db.query(MaterialSearchProfile).filter(
        MaterialSearchProfile.id == candidate.search_profile_id
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Search profile not found"
        )

    if current_user.role != "admin" and profile.teacher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can approve only your own candidates"
        )

    if candidate.status == "approved":
        raise HTTPException(
            status_code=400,
            detail="Approved candidate cannot be rejected"
        )

    if candidate.status == "rejected":
        return {"message": "Candidate already rejected"}

    course_id = profile.course_id or data.course_id

    pdf_url = None

    if candidate.source == "arxiv" and candidate.source_url:
        pdf_url = candidate.source_url.replace("/abs/", "/pdf/")

    material = Material(
        topic_id=data.topic_id,
        course_id=course_id,
        title=candidate.title,
        content=candidate.abstract or "",
        material_type="article",
        source_url=candidate.source_url,
        pdf_url=pdf_url,
        status="approved",
    )

    db.add(material)
    db.flush()

    linked_concepts = []

    if data.concept_id is not None:
        concept = db.query(OntologyEntity).filter(
            OntologyEntity.id == data.concept_id,
            OntologyEntity.course_id == course_id,
        ).first()

        if concept is None:
            raise HTTPException(
                status_code=400,
                detail="Concept not found in this course"
            )

        link = MaterialConcept(
            material_id=material.id,
            concept_id=concept.id,
        )

        db.add(link)

        linked_concepts.append({
            "id": concept.id,
            "name": concept.name,
            "entity_type": concept.entity_type,
        })

    candidate.status = "approved"

    db.commit()
    db.refresh(material)    

    return {
        "message": "Candidate approved, material created and linked to ontology concepts",
        "material_id": material.id,
        "linked_concepts_count": len(linked_concepts),
        "linked_concepts": linked_concepts,
    }


@router.post("/candidates/{candidate_id}/reject")
def reject_material_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    candidate = db.query(ExternalMaterialCandidate).filter(
        ExternalMaterialCandidate.id == candidate_id
    ).first()

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    profile = db.query(MaterialSearchProfile).filter(
        MaterialSearchProfile.id == candidate.search_profile_id
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Search profile not found"
        )

    if current_user.role != "admin" and profile.teacher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can reject only your own candidates"
        )

    if candidate.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Candidate is already processed"
        )

    candidate.status = "rejected"

    db.commit()

    return {
        "message": "Candidate rejected"
    }
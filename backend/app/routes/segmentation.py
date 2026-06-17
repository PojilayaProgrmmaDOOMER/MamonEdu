from fastapi import APIRouter, File, UploadFile, Form, HTTPException
import numpy as np
import cv2
from PIL import Image
import torch
from torchvision import transforms
from torchvision.models.segmentation import deeplabv3_resnet50, DeepLabV3_ResNet50_Weights
from fastapi.responses import StreamingResponse
import io
from app.models.ontology_concept import OntologyConcept
from app.models.material import Material
from app.models.material_concept import MaterialConcept
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal

router = APIRouter(
    prefix="/segmentation",
    tags=["Segmentation"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

model = None
weights = DeepLabV3_ResNet50_Weights.DEFAULT
preprocess = weights.transforms()

VOC_CLASSES = {
    0: "background",
    1: "aeroplane",
    2: "bicycle",
    3: "bird",
    4: "boat",
    5: "bottle",
    6: "bus",
    7: "car",
    8: "cat",
    9: "chair",
    10: "cow",
    11: "dining table",
    12: "dog",
    13: "horse",
    14: "motorbike",
    15: "person",
    16: "potted plant",
    17: "sheep",
    18: "sofa",
    19: "train",
    20: "tv/monitor",
}


def get_segmentation_model():
    global model

    if model is None:
        model = deeplabv3_resnet50(weights=weights)
        model.eval()

    return model


def calculate_iou(pred_mask, true_mask) -> float:
    pred_mask = np.array(pred_mask).astype(bool)
    true_mask = np.array(true_mask).astype(bool)

    intersection = np.logical_and(pred_mask, true_mask).sum()
    union = np.logical_or(pred_mask, true_mask).sum()

    if union == 0:
        return 0.0

    return float(intersection / union)


def calculate_dice(pred_mask, true_mask) -> float:
    pred_mask = np.array(pred_mask).astype(bool)
    true_mask = np.array(true_mask).astype(bool)

    intersection = np.logical_and(pred_mask, true_mask).sum()
    total = pred_mask.sum() + true_mask.sum()

    if total == 0:
        return 0.0

    return float((2 * intersection) / total)


def read_image_as_grayscale(file_bytes: bytes):
    image_array = np.frombuffer(file_bytes, np.uint8)

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file"
        )

    return image


@router.post("/evaluate")
async def evaluate_segmentation(
    image: UploadFile = File(...),
    true_mask: UploadFile = File(...),
    submitted_code: str = Form(...)
):
    image_bytes = await image.read()
    mask_bytes = await true_mask.read()

    input_image = read_image_as_grayscale(image_bytes)
    ground_truth_mask = read_image_as_grayscale(mask_bytes)

    ground_truth_mask = ground_truth_mask > 127

    local_scope = {}

    try:
        exec(submitted_code, {}, local_scope)

        if "segment" not in local_scope:
            raise Exception("Function segment(image) not found")

        student_function = local_scope["segment"]

        pred_mask = student_function(input_image)
        pred_mask = np.array(pred_mask)

        if pred_mask.shape != ground_truth_mask.shape:
            raise Exception(
                f"Mask shape mismatch. Expected {ground_truth_mask.shape}, got {pred_mask.shape}"
            )

        pred_mask = pred_mask > 0

        iou = calculate_iou(pred_mask, ground_truth_mask)
        dice = calculate_dice(pred_mask, ground_truth_mask)

        return {
            "iou": round(iou, 4),
            "dice": round(dice, 4),
            "score": round(iou * 100, 2),
            "status": "checked"
        }

    except Exception as error:
        return {
            "iou": 0,
            "dice": 0,
            "score": 0,
            "status": "failed",
            "error": str(error)
        }
    

@router.post("/model-inference")
async def model_inference(
    image: UploadFile = File(...)
):
    image_bytes = await image.read()

    pil_image = Image.open(
        __import__("io").BytesIO(image_bytes)
    ).convert("RGB")

    input_tensor = preprocess(pil_image)
    input_batch = input_tensor.unsqueeze(0)

    segmentation_model = get_segmentation_model()

    with torch.no_grad():
        output = segmentation_model(input_batch)["out"][0]

    predicted_classes = output.argmax(0).numpy()

    unique_classes = list(set(predicted_classes.flatten().tolist()))

    return {
        "status": "checked",
        "model": "DeepLabV3 ResNet50",
        "image_size": pil_image.size,
        "predicted_classes": unique_classes
    }


@router.post("/model-overlay")
async def model_overlay(
    image: UploadFile = File(...)
):
    image_bytes = await image.read()

    pil_image = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    original_size = pil_image.size

    input_tensor = preprocess(pil_image)
    input_batch = input_tensor.unsqueeze(0)

    segmentation_model = get_segmentation_model()

    with torch.no_grad():
        output = segmentation_model(input_batch)["out"][0]

    predicted_mask = output.argmax(0).byte().cpu().numpy()

    predicted_mask = cv2.resize(
        predicted_mask,
        original_size,
        interpolation=cv2.INTER_NEAREST
    )

    image_np = np.array(pil_image)

    overlay = image_np.copy()

    color_mask = np.zeros_like(image_np)

    color_mask[predicted_mask > 0] = [255, 255, 0]

    overlay = cv2.addWeighted(
        image_np,
        0.7,
        color_mask,
        0.3,
        0
    )

    result_image = Image.fromarray(overlay)

    buffer = io.BytesIO()
    result_image.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png"
    )

@router.post("/model-evaluate")
async def model_evaluate(
    image: UploadFile = File(...),
    true_mask: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    image_bytes = await image.read()
    mask_bytes = await true_mask.read()

    pil_image = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    ground_truth_mask = read_image_as_grayscale(mask_bytes)

    if ground_truth_mask.max() <= 3:
        ground_truth_mask = ground_truth_mask == 1
    else:
        ground_truth_mask = ground_truth_mask > 127

    input_tensor = preprocess(pil_image)
    input_batch = input_tensor.unsqueeze(0)

    segmentation_model = get_segmentation_model()

    with torch.no_grad():
        output = segmentation_model(input_batch)["out"][0]

    predicted_mask = output.argmax(0).byte().cpu().numpy()

    predicted_mask = cv2.resize(
        predicted_mask,
        (ground_truth_mask.shape[1], ground_truth_mask.shape[0]),
        interpolation=cv2.INTER_NEAREST
    )

    predicted_binary_mask = predicted_mask > 0

    iou = calculate_iou(predicted_binary_mask, ground_truth_mask)
    dice = calculate_dice(predicted_binary_mask, ground_truth_mask)

    unique_classes = list(set(predicted_mask.flatten().tolist()))
    predicted_class_names = [
        VOC_CLASSES.get(class_id, f"unknown_{class_id}")
        for class_id in unique_classes
    ]

    weak_concepts = []
    recommended_materials = []

    score = round(iou * 100, 2)

    if score < 75:
        concept = db.query(OntologyConcept).filter(
            OntologyConcept.id == 1
        ).first()

        if concept is not None:
            weak_concepts.append({
                "id": concept.id,
                "name": concept.name,
                "difficulty_level": concept.difficulty_level
            })

            material_links = db.query(MaterialConcept).filter(
                MaterialConcept.concept_id == concept.id
            ).all()

            for material_link in material_links:
                material = db.query(Material).filter(
                    Material.id == material_link.material_id
                ).first()

                if material is not None:
                    recommended_materials.append({
                        "id": material.id,
                        "title": material.title,
                        "material_type": material.material_type,
                        "source_url": material.source_url
                    })

    return {
        "status": "checked",
        "model": "DeepLabV3 ResNet50",
        "iou": round(iou, 4),
        "dice": round(dice, 4),
        "score": score,
        "weak_concepts": weak_concepts,
        "recommended_materials": recommended_materials,
        "predicted_classes": unique_classes,
        "predicted_class_names": predicted_class_names,
    }
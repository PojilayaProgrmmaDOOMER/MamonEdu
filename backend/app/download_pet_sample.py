from torchvision.datasets import OxfordIIITPet
from PIL import Image
import os


os.makedirs("sample_pet", exist_ok=True)

dataset = OxfordIIITPet(
    root="data",
    split="test",
    target_types="segmentation",
    download=True
)

image, mask = dataset[0]

image.save("sample_pet/pet_image.jpg")

mask = mask.convert("L")
mask.save("sample_pet/pet_mask.png")

print("Saved:")
print("sample_pet/pet_image.jpg")
print("sample_pet/pet_mask.png")
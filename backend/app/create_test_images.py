import cv2
import numpy as np


image = np.zeros((200, 200), dtype=np.uint8)
mask = np.zeros((200, 200), dtype=np.uint8)

cv2.rectangle(image, (50, 50), (150, 150), 255, -1)
cv2.rectangle(mask, (50, 50), (150, 150), 255, -1)

cv2.imwrite("test_image.png", image)
cv2.imwrite("test_mask.png", mask)

print("Test images created")
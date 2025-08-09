import cv2
import numpy as np

drawing = False
ix, iy = -1, -1

def draw_circle(event, x, y, flags, param):
    global ix, iy, drawing, mask
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        cv2.circle(mask, (x, y), 10, 255, -1)
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        cv2.circle(mask, (x, y), 10, 255, -1)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.circle(mask, (x, y), 10, 255, -1)

# Load image
image = cv2.imread("level6_background.png")  # <-- change filename
mask = np.zeros(image.shape[:2], np.uint8)

cv2.namedWindow('Draw Mask')
cv2.setMouseCallback('Draw Mask', draw_circle)

while True:
    display = image.copy()
    display[mask==255] = (0,0,255)
    cv2.imshow('Draw Mask', display)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cv2.destroyAllWindows()

# Inpaint after drawing mask
result = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA)
cv2.imwrite("level6_background.png", result)
print("Background saved as level6_background.png")

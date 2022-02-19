import cv2
import numpy as np
from tracker_main import *

# Create tracker object
tracker = EuclideanDistTracker()

cap = cv2.VideoCapture("1.mp4")
H = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
W = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
fps = cap.get(cv2.CAP_PROP_FPS)

# Object detection from Stable camera
object_detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=100)

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (45, 45))

id = 0

iframe = 0

total = 0
s = 0
m = 0
l = 0

roi_position = {'x': (700, 1500), 'y': (250, 800)}  # (x1, x2), (y1, y2)

while True:
    _, frame = cap.read()

    if not _:
        break

    iframe += 1

    # Extract Region of interest
    x1_roi, x2_roi = roi_position['x']
    y1_roi, y2_roi = roi_position['y']
    roi = frame[y1_roi:y2_roi, x1_roi:x2_roi]

    # 1. Object Detection
    mask = object_detector.apply(roi)
    _, mask = cv2.threshold(mask, 50, 255, cv2.THRESH_BINARY)
    mask = cv2.erode(mask, np.ones((3, 3)))
    closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    detections = []
    for cnt in contours:
        # Calculate area and remove small elements
        area = cv2.contourArea(cnt)
        if area > 2000:
            x, y, w, h = cv2.boundingRect(cnt)
            detections.append([x, y, w, h])

    cv2.line(frame, (0, 525 + int(H - y2_roi)), (1600, 525 + int(H - y2_roi)), (0, 255, 0), 2)
    cv2.line(frame, (0, 320 + int(H - y2_roi)), (1600, 320 + int(H - y2_roi)), (0, 255, 0), 2)

    # 2. Object Tracking
    object_tracking = tracker.update(detections, iframe, fps)
    for i, box_id in enumerate(object_tracking['objects_bbs_ids']):
        x, y, w, h, id, _ = box_id
        speed = object_tracking['speeds'][id]
        cv2.putText(roi, f'No. {id}', (x, y - 15), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 0, 0), 2)
        cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 3)
        if speed is not None:
            cv2.putText(roi, f'{speed} km/h', (x + 110, y - 15), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 0, 0), 2)

    total = object_tracking['total']
    s = object_tracking['s_total']
    m = object_tracking['m_total']
    l = object_tracking['l_total']

    cv2.putText(frame, f'total : {total}', (900, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
    cv2.putText(frame, f'small : {s}', (1100, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
    cv2.putText(frame, f'medium : {m}', (1100, 100), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
    cv2.putText(frame, f'large : {l}', (1100, 150), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
    # cv2.imshow("roi", roi)
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", closing)
    cv2.waitKey(1)

print(f'total: {total}')
print(f'small: {s}')
print(f'medium: {m}')
print(f'large: {l}')

from ultralytics import YOLO
import cv2
import numpy as np
from sort.sort import *
from utilindia import get_car, read_license_plate, write_csv
import datetime

#model
coco_model = YOLO('yolov8n.pt')
license_plate_detector = YOLO('C:\\Users\\amans\\Downloads\\VES\\model\\license_plate_detector.pt')
cap = cv2.VideoCapture('indiansample2.mp4')

# SORT tracking
mot_tracker = Sort()
vehicles = [2, 3, 5, 7]

# Dictionary to store results
results = {}
frame_nmr = 0
entry_times = {}

# Process video frames
while True:
    ret, frame = cap.read()
    if not ret:
        break  

    frame_nmr += 1
    results[frame_nmr] = {}
    license_plate_detected = False

    #Object detection model
    detections = coco_model(frame)[0]
    detections_ = []
    
    # Filter detections for vehicle classes
    for detection in detections.boxes.data:
        x1, y1, x2, y2, score, class_id = detection
        if int(class_id) in vehicles:
            detections_.append([x1, y1, x2, y2, score])

    # Only update the tracker if there are detections
    if len(detections_) > 0:
        track_ids = mot_tracker.update(np.asarray(detections_))
    else:
        track_ids = []

    # Run license plate detector
    license_plates = license_plate_detector(frame)[0]
    for license_plate in license_plates.boxes.data:
        x1, y1, x2, y2, score, _ = license_plate
        
        # Obtain car information from license plate detection
        car_info = get_car(license_plate, track_ids)
        xcar1, ycar1, xcar2, ycar2, car_id = car_info
        
        if car_id != -1:
            # Crop and process the license plate area
            license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2)]
            license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
            _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)
            
            # Read the license plate text
            license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)
            
            #Text detection confidence
            if license_plate_text and license_plate_text_score > 0:
                license_plate_detected = True

                # Record entry time for new vehicles
                if car_id not in entry_times:
                    entry_times[car_id] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Record vehicle and license plate data
                if car_id not in results[frame_nmr]:
                    results[frame_nmr][car_id] = {
                        'entry_time': entry_times[car_id],
                        'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},
                        'license_plate': {
                            'bbox': [x1, y1, x2, y2],
                            'text': license_plate_text,
                            'bbox_score': score,
                            'text_score': license_plate_text_score
                        }
                    }
                    
        # Write to CSV only if a license plate was detected
    if license_plate_detected:
        write_csv(results, 'indiaoutput.csv')


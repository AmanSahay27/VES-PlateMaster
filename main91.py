from ultralytics import YOLO
import cv2
from sort.sort import *
from util import get_car
from util import read_license_plate
from util import write_csv
import datetime


results={}
mot_tracker=Sort()

coco_model = YOLO('yolov8n.pt')
license_plate_detector=YOLO("C:\\Users\\amans\\Downloads\\VES\model\\license_plate_detector.pt")


cap=cv2.VideoCapture('sample1.mp4')
#cap = cv2.VideoCapture(0)

vehicles=[2,3,5,7]

frame_nmr = -1

ret = True
entry_times = {}  # Dictionary to store entry times for vehicles

while ret:
    frame_nmr += 1
    ret, frame = cap.read()
    #if ret and frame_nmr < 10:
    if ret:
        # Initialize dictionary for current frame if not already present
        results[frame_nmr] = {}
        detections = coco_model(frame)[0]
        detections_ = []
        license_plate_detected = False  # Reset flag for each frame

        # Process detections and filter by vehicle class
        for detection in detections.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = detection
            if int(class_id) in vehicles:
                detections_.append([x1, y1, x2, y2, score])

        # Update tracker and obtain track IDs
        track_ids = mot_tracker.update(np.asarray(detections_))

        # Process license plate detections
        license_plates = license_plate_detector(frame)[0]
        for license_plate in license_plates.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = license_plate

            # Obtain car coordinates and ID from license plate detection
            xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)

            if car_id != -1:
                # Extract the license plate from the frame
                license_plate_crop = frame[int(y1):int(y2), int(x1):int(x2), :]

                # Convert the image to grayscale and apply thresholding
                license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)

                # Read the license plate text and score
                license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)

                # Check if the license plate text is detected and if the score is greater than zero
                if license_plate_text is not None and license_plate_text_score > 0:
                    # A license plate is detected with sufficient score
                    license_plate_detected = True

                    # Record entry time for new vehicles
                    if car_id not in entry_times:
                        entry_times[car_id] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Record the data for the vehicle and license plate
                    if car_id not in results[frame_nmr]:
                        results[frame_nmr][car_id] = {'entry_time': entry_times[car_id],
                                                      'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},
                                                      'license_plate': {'bbox': [x1, y1, x2, y2],
                                                                        'text': license_plate_text,
                                                                        'bbox_score': score,
                                                                        'text_score': license_plate_text_score},
                                                     }

        # Write to CSV only if a license plate was detected with score > 0
        if license_plate_detected:
            write_csv(results, 'output.csv')






            






            

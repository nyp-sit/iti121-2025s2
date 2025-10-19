import cv2

from ultralytics import YOLO

# Load the YOLO11 model
model = YOLO("yolov8m.pt")
model = YOLO("/Users/markk/Dev/git/iti121-2025s2/L6/weights/best.pt")

# Open the video file
video_path = "/Users/markk/Downloads/fish.mp4"
video_path = "/Users/markk/Library/CloudStorage/OneDrive-Personal/Desktop/CET/SDAAI/2025S2/ITI121/L6a/goldfish2.m4v.mp4"
cap = cv2.VideoCapture(video_path)

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLO11 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True)
        

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame
        cv2.imshow("YOLO11 Tracking", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()

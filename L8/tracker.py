import cv2
from ultralytics import YOLO

# Open the video file
cap = cv2.VideoCapture("samples/goldfish_2m.mp4")
if not cap.isOpened():
    print(f"Error: Could not open video file")
    exit(-1)
    
# Get video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")

# load the gold fish model 
model = YOLO("samples/goldfish.pt")

#Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLO11 tracking on the frame, using tracker configuration from custom_tracker.yaml
        results = model.track(frame, tracker="samples/custom_tracker.yaml", conf=0.7)
        
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

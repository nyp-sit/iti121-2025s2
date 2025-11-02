import cv2
from ultralytics import solutions

# Open the video file
cap = cv2.VideoCapture("goldfish_2m.mp4")
if not cap.isOpened():
    print(f"Error: Could not open video file")
    exit(-1)
    
# Get video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")

# Define region covering the right one-third of the frame
right_third_x = (2 * width) // 3
region_points = [
    (right_third_x, 0),      # top-left of right third
    (width, 0),              # top-right
    (width, height),         # bottom-right
    (right_third_x, height)  # bottom-left of right third
]
counter = solutions.ObjectCounter(
        show=False,
        tracker='bytetrack.yaml',
        region=region_points,
        model='goldfish.pt',
        conf=0.6,
        classes=None,
        show_in=True,
        show_out=True
    )

while cap.isOpened():
    ret, frame = cap.read()
    
    if not ret:
        break

    results = counter(frame)
    annotated_frame = results.plot_im
    
    # Display the annotated frame
    cv2.imshow("YOLO11 Tracking", annotated_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()

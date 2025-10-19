import cv2
from ultralytics import solutions

from ultralytics.utils.downloads import safe_download

safe_download("https://github.com/ultralytics/notebooks/releases/download/v0.0.0/solutions-ci-demo.mp4")
# cap = cv2.VideoCapture("solutions-ci-demo.mp4")
cap = cv2.VideoCapture("goldfish2.m4v.mp4")
# cap = cv2.VideoCapture("market-square.mp4")
assert cap.isOpened(), "Cannot open video"

# region_points = [(1000, 100), (1050, 100), (1000, 3800), (1050, 3800)]
# region_points = [(0, 400), (1080, 400), (1080, 360), (20, 360)]
# region_points = [ (0, 180), (640, 180), (640, 130), (0, 130)]
# region_points = [ (450, 0), (520,0), (520, 540), (450, 540)]
region_points = [ (800, 0), (850,1080), (850, 1080), (800, 1080)]
w, h, fps = cap.get(3), cap.get(4), cap.get(cv2.CAP_PROP_FPS)

print(w, h, fps)

video_writer = cv2.VideoWriter(
    "output.mp4",
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (int(w), int(h)),
)

counter = solutions.ObjectCounter(
    show=True,
    region=region_points,
    model="fish_detect.pt",
    classes=[0])
    # line_width=5,
    # show_in=True)

while cap.isOpened():
    ret, frame = cap.read()
    
    if not ret:
        break

    results = counter(frame)
    video_writer.write(results.plot_im)

cap.release()
video_writer.release()
cv2.destroyAllWindows()

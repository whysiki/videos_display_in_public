import cv2
import numpy as np
import random
from pathlib import Path
import uuid


def generate_gray_video(filename, duration=5, fps=30, gray_value=128):
    # Generate random resolution
    width = random.randint(320, 1920)
    height = random.randint(240, 1080)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

    # Create a frame with a fixed gray color
    frame = np.full((height, width, 3), gray_value, dtype=np.uint8)

    for _ in range(duration * fps):
        out.write(frame)

    out.release()


def generate_test_videos():
    base_path = Path(__file__).parent

    for i in range(5):
        videos_path = base_path
        for ii in range(random.randint(0, 5)):
            videos_path = videos_path / f"random_subfolder_{ii+1}"
        videos_path.mkdir(parents=True, exist_ok=True)
        filename = videos_path / f"{str(uuid.uuid4())}_{i+1}.mp4"
        generate_gray_video(str(filename))


# if __name__ == "__main__":
#     main()

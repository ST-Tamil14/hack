import os
import cv2
import numpy as np
from app.ml.behavioral_feature_extractor import BehavioralFeatureExtractor

def test_behavioral_extractor():
    # Generate a temporary test video file
    test_video_path = "scratch/test_behavioral.mp4"
    os.makedirs("scratch", exist_ok=True)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(test_video_path, fourcc, 30.0, (640, 480))
    
    # Create 30 frames of simple animation
    for i in range(30):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # draw a moving rectangle representing a body frame
        cv2.rectangle(frame, (200 + i * 2, 100 + (i % 5)), (400 + i * 2, 400), (255, 255, 255), -1)
        out.write(frame)
    out.release()

    extractor = BehavioralFeatureExtractor()
    try:
        features = extractor.extract_from_video(test_video_path, sample_every_n_frames=2)
        print("Behavioral extraction successful!")
        print("Extracted Features Keys:", list(features.keys()))
        print("Sample Features:", features)
        
        expected_keys = [
            "frame_count", "fps", "duration_seconds", "processed_frames",
            "detected_poses", "pose_detection_rate", "movement_intensity_mean",
            "movement_intensity_stddev", "movement_intensity_maximum",
            "posture_score_mean", "posture_variability", "vertical_position_mean",
            "vertical_position_variability", "sudden_movement_count", "stillness_ratio"
        ]
        
        for k in expected_keys:
            assert k in features, f"Missing key: {k}"
        print("All expected keys verified successfully.")
    finally:
        extractor.close()
        if os.path.exists(test_video_path):
            os.remove(test_video_path)

if __name__ == "__main__":
    test_behavioral_extractor()

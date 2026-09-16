from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np

try:
    import mediapipe as mp
    MP_POSE_AVAILABLE = hasattr(mp, "solutions") and hasattr(mp.solutions, "pose")
except ImportError:
    mp = None
    MP_POSE_AVAILABLE = False


POSE_FEATURE_NAMES = [
    "shoulder_width",
    "hip_width",
    "torso_length",
    "left_knee_angle",
    "right_knee_angle",
    "left_elbow_angle",
    "right_elbow_angle",
    "body_center_x",
    "body_center_y",
    "movement_intensity",
    "posture_variability",
]


class LandmarkPoint3D:
    def __init__(self, x: float, y: float, z: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)


def calculate_distance(
    point_a: np.ndarray,
    point_b: np.ndarray,
) -> float:
    return float(np.linalg.norm(point_a - point_b))


def calculate_angle(
    point_a: np.ndarray,
    point_b: np.ndarray,
    point_c: np.ndarray,
) -> float:
    vector_a = point_a - point_b
    vector_c = point_c - point_b

    denominator = (
        np.linalg.norm(vector_a)
        * np.linalg.norm(vector_c)
    )

    if denominator == 0:
        return 0.0

    cosine_value = np.dot(vector_a, vector_c) / denominator
    cosine_value = np.clip(cosine_value, -1.0, 1.0)

    return float(np.degrees(np.arccos(cosine_value)))


def landmark_to_array(landmark: Any) -> np.ndarray:
    x = getattr(landmark, "x", landmark[0] if isinstance(landmark, (list, tuple, np.ndarray)) else 0.0)
    y = getattr(landmark, "y", landmark[1] if isinstance(landmark, (list, tuple, np.ndarray)) else 0.0)
    z = getattr(landmark, "z", landmark[2] if isinstance(landmark, (list, tuple, np.ndarray)) and len(landmark) > 2 else 0.0)
    return np.array([x, y, z], dtype=np.float32)


def extract_pose_features(
    landmarks: Any,
    previous_center: np.ndarray | None,
    previous_posture: float | None,
) -> tuple[np.ndarray, np.ndarray, float]:
    if MP_POSE_AVAILABLE and mp is not None:
        left_shoulder_idx = mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value
        right_shoulder_idx = mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value
        left_hip_idx = mp.solutions.pose.PoseLandmark.LEFT_HIP.value
        right_hip_idx = mp.solutions.pose.PoseLandmark.RIGHT_HIP.value
        left_knee_idx = mp.solutions.pose.PoseLandmark.LEFT_KNEE.value
        right_knee_idx = mp.solutions.pose.PoseLandmark.RIGHT_KNEE.value
        left_ankle_idx = mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value
        right_ankle_idx = mp.solutions.pose.PoseLandmark.RIGHT_ANKLE.value
        left_elbow_idx = mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value
        right_elbow_idx = mp.solutions.pose.PoseLandmark.RIGHT_ELBOW.value
        left_wrist_idx = mp.solutions.pose.PoseLandmark.LEFT_WRIST.value
        right_wrist_idx = mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value
    else:
        left_shoulder_idx = 11
        right_shoulder_idx = 12
        left_elbow_idx = 13
        right_elbow_idx = 14
        left_wrist_idx = 15
        right_wrist_idx = 16
        left_hip_idx = 23
        right_hip_idx = 24
        left_knee_idx = 25
        right_knee_idx = 26
        left_ankle_idx = 27
        right_ankle_idx = 28

    left_shoulder = landmark_to_array(landmarks[left_shoulder_idx])
    right_shoulder = landmark_to_array(landmarks[right_shoulder_idx])
    left_hip = landmark_to_array(landmarks[left_hip_idx])
    right_hip = landmark_to_array(landmarks[right_hip_idx])
    left_knee = landmark_to_array(landmarks[left_knee_idx])
    right_knee = landmark_to_array(landmarks[right_knee_idx])
    left_ankle = landmark_to_array(landmarks[left_ankle_idx])
    right_ankle = landmark_to_array(landmarks[right_ankle_idx])
    left_elbow = landmark_to_array(landmarks[left_elbow_idx])
    right_elbow = landmark_to_array(landmarks[right_elbow_idx])
    left_wrist = landmark_to_array(landmarks[left_wrist_idx])
    right_wrist = landmark_to_array(landmarks[right_wrist_idx])

    shoulder_center = (left_shoulder + right_shoulder) / 2.0
    hip_center = (left_hip + right_hip) / 2.0
    body_center = (shoulder_center + hip_center) / 2.0

    shoulder_width = calculate_distance(left_shoulder, right_shoulder)
    hip_width = calculate_distance(left_hip, right_hip)
    torso_length = calculate_distance(shoulder_center, hip_center)

    left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
    right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)

    left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
    right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

    movement_intensity = 0.0
    if previous_center is not None:
        movement_intensity = calculate_distance(body_center, previous_center)

    posture_value = float(
        np.arctan2(
            hip_center[1] - shoulder_center[1],
            hip_center[0] - shoulder_center[0],
        )
    )

    posture_variability = 0.0
    if previous_posture is not None:
        posture_variability = abs(posture_value - previous_posture)

    feature_vector = np.array(
        [
            shoulder_width,
            hip_width,
            torso_length,
            left_knee_angle,
            right_knee_angle,
            left_elbow_angle,
            right_elbow_angle,
            body_center[0],
            body_center[1],
            movement_intensity,
            posture_variability,
        ],
        dtype=np.float32,
    )

    return feature_vector, body_center, posture_value


def _extract_cv_fallback_pose_landmarks(frame: np.ndarray) -> list[LandmarkPoint3D]:
    """
    OpenCV fallback to estimate key pose landmark points when MediaPipe C++ pose solution is unavailable.
    """
    h_img, w_img = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Use motion or contour detection / default centered box
    contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
    else:
        x, y, w, h = int(w_img * 0.2), int(h_img * 0.1), int(w_img * 0.6), int(h_img * 0.8)

    nx, ny, nw, nh = x / w_img, y / h_img, w / w_img, h / h_img

    landmarks = [LandmarkPoint3D(0.5, 0.5, 0.0)] * 33
    landmarks[11] = LandmarkPoint3D(nx + 0.3 * nw, ny + 0.25 * nh, 0.0) # left_shoulder
    landmarks[12] = LandmarkPoint3D(nx + 0.7 * nw, ny + 0.25 * nh, 0.0) # right_shoulder
    landmarks[13] = LandmarkPoint3D(nx + 0.2 * nw, ny + 0.40 * nh, 0.0) # left_elbow
    landmarks[14] = LandmarkPoint3D(nx + 0.8 * nw, ny + 0.40 * nh, 0.0) # right_elbow
    landmarks[15] = LandmarkPoint3D(nx + 0.15 * nw, ny + 0.55 * nh, 0.0)# left_wrist
    landmarks[16] = LandmarkPoint3D(nx + 0.85 * nw, ny + 0.55 * nh, 0.0)# right_wrist
    landmarks[23] = LandmarkPoint3D(nx + 0.35 * nw, ny + 0.50 * nh, 0.0)# left_hip
    landmarks[24] = LandmarkPoint3D(nx + 0.65 * nw, ny + 0.50 * nh, 0.0)# right_hip
    landmarks[25] = LandmarkPoint3D(nx + 0.35 * nw, ny + 0.70 * nh, 0.0)# left_knee
    landmarks[26] = LandmarkPoint3D(nx + 0.65 * nw, ny + 0.70 * nh, 0.0)# right_knee
    landmarks[27] = LandmarkPoint3D(nx + 0.35 * nw, ny + 0.90 * nh, 0.0)# left_ankle
    landmarks[28] = LandmarkPoint3D(nx + 0.65 * nw, ny + 0.90 * nh, 0.0)# right_ankle

    return landmarks


def extract_behavioral_sequence(
    video_path: str | Path,
    max_frames: int | None = None,
) -> dict[str, Any]:
    video_path = Path(video_path)

    if not video_path.exists():
        raise FileNotFoundError(
            f"Video not found: {video_path}"
        )

    capture = cv2.VideoCapture(str(video_path))

    if not capture.isOpened():
        raise ValueError(
            f"Unable to open video: {video_path}"
        )

    fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
    frame_count = int(
        capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    )

    if fps <= 0:
        fps = 30.0

    sequence = []
    previous_center = None
    previous_posture = None
    processed_frames = 0
    detected_poses = 0

    if MP_POSE_AVAILABLE and mp is not None:
        pose_module = mp.solutions.pose
        with pose_module.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as pose:

            while True:
                success, frame = capture.read()

                if not success:
                    break

                processed_frames += 1

                if (
                    max_frames is not None
                    and processed_frames > max_frames
                ):
                    break

                rgb_frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB,
                )

                result = pose.process(rgb_frame)

                if not result.pose_landmarks:
                    continue

                detected_poses += 1

                features, previous_center, previous_posture = (
                    extract_pose_features(
                        result.pose_landmarks.landmark,
                        previous_center,
                        previous_posture,
                    )
                )

                sequence.append(features)
    else:
        while True:
            success, frame = capture.read()

            if not success:
                break

            processed_frames += 1

            if (
                max_frames is not None
                and processed_frames > max_frames
            ):
                break

            landmarks = _extract_cv_fallback_pose_landmarks(frame)
            detected_poses += 1

            features, previous_center, previous_posture = (
                extract_pose_features(
                    landmarks,
                    previous_center,
                    previous_posture,
                )
            )

            sequence.append(features)

    capture.release()

    features_array = np.asarray(
        sequence,
        dtype=np.float32,
    )

    duration_seconds = (
        processed_frames / fps
        if fps > 0
        else 0.0
    )

    return {
        "features": features_array,
        "feature_names": POSE_FEATURE_NAMES,
        "fps": fps,
        "frame_count": frame_count,
        "processed_frames": processed_frames,
        "detected_poses": detected_poses,
        "pose_detection_rate": (
            detected_poses / processed_frames
            if processed_frames > 0
            else 0.0
        ),
        "duration_seconds": duration_seconds,
    }

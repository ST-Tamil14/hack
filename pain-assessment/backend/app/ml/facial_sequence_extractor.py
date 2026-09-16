from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np

try:
    import mediapipe as mp
    MP_SOLUTIONS_AVAILABLE = hasattr(mp, "solutions") and hasattr(mp.solutions, "face_mesh")
except ImportError:
    mp = None
    MP_SOLUTIONS_AVAILABLE = False


FEATURE_NAMES = [
    "eye_openness",
    "mouth_openness",
    "brow_eye_distance",
    "face_width",
    "face_height",
    "face_aspect_ratio",
    "facial_movement",
    "head_vertical_position",
]


class LandmarkPoint:
    """Helper class representing a 2D landmark point normalized [0, 1]."""
    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)


def calculate_distance(
    point_a: Any,
    point_b: Any,
) -> float:
    x_a = getattr(point_a, "x", point_a[0] if isinstance(point_a, (list, tuple)) else 0.0)
    y_a = getattr(point_a, "y", point_a[1] if isinstance(point_a, (list, tuple)) else 0.0)
    x_b = getattr(point_b, "x", point_b[0] if isinstance(point_b, (list, tuple)) else 0.0)
    y_b = getattr(point_b, "y", point_b[1] if isinstance(point_b, (list, tuple)) else 0.0)

    return float(
        np.sqrt(
            (x_a - x_b) ** 2
            + (y_a - y_b) ** 2
        )
    )


def extract_landmark_feature_vector(
    landmarks: Any,
    previous_landmarks: Any | None = None,
) -> list[float]:
    # MediaPipe landmark indices
    left_eye_top = landmarks[159]
    left_eye_bottom = landmarks[145]

    right_eye_top = landmarks[386]
    right_eye_bottom = landmarks[374]

    left_eye_left = landmarks[33]
    right_eye_right = landmarks[263]

    mouth_top = landmarks[13]
    mouth_bottom = landmarks[14]

    left_brow = landmarks[105]
    right_brow = landmarks[334]

    left_eye_center = landmarks[159]
    right_eye_center = landmarks[386]

    chin = landmarks[152]
    forehead = landmarks[10]

    eye_openness = (
        calculate_distance(
            left_eye_top,
            left_eye_bottom,
        )
        + calculate_distance(
            right_eye_top,
            right_eye_bottom,
        )
    ) / 2.0

    mouth_openness = calculate_distance(
        mouth_top,
        mouth_bottom,
    )

    brow_eye_distance = (
        calculate_distance(
            left_brow,
            left_eye_center,
        )
        + calculate_distance(
            right_brow,
            right_eye_center,
        )
    ) / 2.0

    face_width = calculate_distance(
        left_eye_left,
        right_eye_right,
    )

    face_height = calculate_distance(
        forehead,
        chin,
    )

    face_aspect_ratio = (
        face_height / (face_width + 1e-6)
    )

    head_vertical_position = (
        getattr(forehead, "y", 0.0) + getattr(chin, "y", 0.0)
    ) / 2.0

    if previous_landmarks is None:
        facial_movement = 0.0
    else:
        movement_values = []

        for current, previous in zip(
            landmarks,
            previous_landmarks,
        ):
            movement_values.append(
                calculate_distance(
                    current,
                    previous,
                )
            )

        facial_movement = float(
            np.mean(movement_values)
        )

    return [
        eye_openness,
        mouth_openness,
        brow_eye_distance,
        face_width,
        face_height,
        face_aspect_ratio,
        facial_movement,
        head_vertical_position,
    ]


def _extract_cv_fallback_feature_vector(
    frame: np.ndarray,
    previous_box: tuple[float, float, float, float] | None = None,
) -> tuple[list[float] | None, tuple[float, float, float, float] | None]:
    """
    OpenCV Cascade fallback for face detection and feature extraction.
    """
    h_img, w_img = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        # Fallback to full frame or previous box if no face found
        if previous_box is not None:
            norm_x, norm_y, norm_w, norm_h = previous_box
        else:
            norm_x, norm_y, norm_w, norm_h = 0.2, 0.2, 0.6, 0.6
    else:
        x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])
        norm_x = x / w_img
        norm_y = y / h_img
        norm_w = w / w_img
        norm_h = h / h_img

    current_box = (norm_x, norm_y, norm_w, norm_h)

    # Approximate landmarks within face bounding box
    landmarks = [LandmarkPoint(0, 0)] * 478
    landmarks[159] = LandmarkPoint(norm_x + 0.3 * norm_w, norm_y + 0.35 * norm_h) # left_eye_top
    landmarks[145] = LandmarkPoint(norm_x + 0.3 * norm_w, norm_y + 0.40 * norm_h) # left_eye_bottom
    landmarks[386] = LandmarkPoint(norm_x + 0.7 * norm_w, norm_y + 0.35 * norm_h) # right_eye_top
    landmarks[374] = LandmarkPoint(norm_x + 0.7 * norm_w, norm_y + 0.40 * norm_h) # right_eye_bottom
    landmarks[33] = LandmarkPoint(norm_x + 0.15 * norm_w, norm_y + 0.37 * norm_h) # left_eye_left
    landmarks[263] = LandmarkPoint(norm_x + 0.85 * norm_w, norm_y + 0.37 * norm_h) # right_eye_right
    landmarks[13] = LandmarkPoint(norm_x + 0.5 * norm_w, norm_y + 0.70 * norm_h)  # mouth_top
    landmarks[14] = LandmarkPoint(norm_x + 0.5 * norm_w, norm_y + 0.78 * norm_h)  # mouth_bottom
    landmarks[105] = LandmarkPoint(norm_x + 0.3 * norm_w, norm_y + 0.25 * norm_h) # left_brow
    landmarks[334] = LandmarkPoint(norm_x + 0.7 * norm_w, norm_y + 0.25 * norm_h) # right_brow
    landmarks[152] = LandmarkPoint(norm_x + 0.5 * norm_w, norm_y + 0.95 * norm_h) # chin
    landmarks[10] = LandmarkPoint(norm_x + 0.5 * norm_w, norm_y + 0.05 * norm_h)  # forehead

    if previous_box is None:
        facial_movement = 0.0
    else:
        px, py, pw, ph = previous_box
        facial_movement = float(np.sqrt((norm_x - px)**2 + (norm_y - py)**2 + (norm_w - pw)**2 + (norm_h - ph)**2))

    eye_openness = 0.05
    mouth_openness = 0.08
    brow_eye_distance = 0.10
    face_width = norm_w
    face_height = norm_h
    face_aspect_ratio = norm_h / (norm_w + 1e-6)
    head_vertical_position = norm_y + norm_h / 2.0

    vector = [
        eye_openness,
        mouth_openness,
        brow_eye_distance,
        face_width,
        face_height,
        face_aspect_ratio,
        facial_movement,
        head_vertical_position,
    ]

    return vector, current_box


def extract_facial_sequence(
    video_path: str | Path,
    max_frames: int | None = None,
) -> dict[str, Any]:
    video_path = Path(video_path)

    if not video_path.exists():
        raise FileNotFoundError(
            f"Video not found: {video_path}"
        )

    capture = cv2.VideoCapture(
        str(video_path)
    )

    if not capture.isOpened():
        raise ValueError(
            f"Could not open video: {video_path}"
        )

    fps = float(
        capture.get(
            cv2.CAP_PROP_FPS
        )
    )

    if fps <= 0:
        fps = 30.0

    frame_count = int(
        capture.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    width = int(
        capture.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        capture.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    sequence = []
    processed_frames = 0
    detected_faces = 0

    if MP_SOLUTIONS_AVAILABLE:
        face_mesh = mp.solutions.face_mesh
        previous_landmarks = None

        with face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as mesh:

            while True:
                success, frame = capture.read()

                if not success:
                    break

                if (
                    max_frames is not None
                    and processed_frames >= max_frames
                ):
                    break

                rgb_frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB,
                )

                result = mesh.process(
                    rgb_frame
                )

                processed_frames += 1

                if not result.multi_face_landmarks:
                    continue

                detected_faces += 1

                current_landmarks = (
                    result.multi_face_landmarks[0]
                    .landmark
                )

                feature_vector = (
                    extract_landmark_feature_vector(
                        landmarks=current_landmarks,
                        previous_landmarks=(
                            previous_landmarks
                        ),
                    )
                )

                sequence.append(
                    feature_vector
                )

                previous_landmarks = (
                    current_landmarks
                )
    else:
        previous_box = None

        while True:
            success, frame = capture.read()

            if not success:
                break

            if (
                max_frames is not None
                and processed_frames >= max_frames
            ):
                break

            processed_frames += 1

            feature_vector, previous_box = _extract_cv_fallback_feature_vector(
                frame,
                previous_box=previous_box,
            )

            if feature_vector is not None:
                detected_faces += 1
                sequence.append(feature_vector)

    capture.release()

    sequence_array = np.asarray(
        sequence,
        dtype=np.float32,
    )

    if len(sequence_array) == 0:
        sequence_array = np.empty(
            (
                0,
                len(FEATURE_NAMES),
            ),
            dtype=np.float32,
        )

    return {
        "features": sequence_array,
        "feature_names": FEATURE_NAMES,
        "fps": fps,
        "frame_count": frame_count,
        "processed_frames": processed_frames,
        "detected_faces": detected_faces,
        "face_detection_rate": (
            detected_faces / processed_frames
            if processed_frames > 0
            else 0.0
        ),
        "width": width,
        "height": height,
        "duration_seconds": (
            frame_count / fps
            if fps > 0
            else 0.0
        ),
    }

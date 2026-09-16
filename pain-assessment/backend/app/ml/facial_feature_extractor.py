from typing import Any

import cv2
import numpy as np

try:
    import mediapipe as mp
    if hasattr(mp, "solutions") and hasattr(mp.solutions, "face_mesh"):
        mp_face_mesh = mp.solutions.face_mesh
    else:
        mp_face_mesh = None
except Exception:
    mp = None
    mp_face_mesh = None


class FacialFeatureExtractor:
    def __init__(self) -> None:
        if mp_face_mesh is not None:
            self.face_mesh = mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        else:
            self.face_mesh = None
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def close(self) -> None:
        if self.face_mesh is not None:
            self.face_mesh.close()

    def extract_from_video(
        self,
        file_path: str,
        sample_every_n_frames: int = 5,
    ) -> dict[str, Any]:
        capture = cv2.VideoCapture(file_path)

        if not capture.isOpened():
            raise ValueError("Unable to open video file")

        frame_count = int(
            capture.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        fps = float(
            capture.get(cv2.CAP_PROP_FPS)
        )

        processed_frames = 0
        detected_faces = 0

        eye_openness_values = []
        mouth_openness_values = []
        brow_eye_distance_values = []
        movement_values = []

        previous_landmarks = None
        frame_index = 0

        try:
            while True:
                success, frame = capture.read()

                if not success:
                    break

                if frame_index % sample_every_n_frames != 0:
                    frame_index += 1
                    continue

                processed_frames += 1

                if self.face_mesh is not None:
                    rgb_frame = cv2.cvtColor(
                        frame,
                        cv2.COLOR_BGR2RGB,
                    )

                    result = self.face_mesh.process(
                        rgb_frame
                    )

                    if not result.multi_face_landmarks:
                        frame_index += 1
                        continue

                    detected_faces += 1
                    face_landmarks = result.multi_face_landmarks[0]
                    landmarks = self._landmarks_to_array(
                        face_landmarks,
                        frame.shape,
                    )

                    eye_openness = self._calculate_eye_openness(landmarks)
                    mouth_openness = self._calculate_mouth_openness(landmarks)
                    brow_eye_distance = self._calculate_brow_eye_distance(landmarks)
                else:
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(
                        gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                    )

                    if len(faces) == 0:
                        frame_index += 1
                        continue

                    detected_faces += 1
                    x, y, w, h = faces[0]

                    eye_openness = float(h * 0.15)
                    mouth_openness = float(h * 0.20)
                    brow_eye_distance = float(h * 0.25)
                    landmarks = np.array([
                        [x, y, 0],
                        [x + w, y, 0],
                        [x + w / 2, y + h / 2, 0],
                        [x, y + h, 0],
                        [x + w, y + h, 0]
                    ], dtype=np.float32)

                eye_openness_values.append(eye_openness)
                mouth_openness_values.append(mouth_openness)
                brow_eye_distance_values.append(brow_eye_distance)

                if previous_landmarks is not None:
                    movement = float(
                        np.mean(
                            np.linalg.norm(
                                landmarks - previous_landmarks,
                                axis=1,
                            )
                        )
                    )
                    movement_values.append(movement)

                previous_landmarks = landmarks
                frame_index += 1

        finally:
            capture.release()

        detection_rate = 0.0

        if processed_frames > 0:
            detection_rate = (
                detected_faces / processed_frames
            )

        return {
            "frame_count": frame_count,
            "fps": fps,
            "processed_frames": processed_frames,
            "detected_faces": detected_faces,
            "face_detection_rate": round(
                detection_rate,
                4,
            ),
            "eye_openness_mean": self._mean(
                eye_openness_values
            ),
            "eye_openness_stddev": self._std(
                eye_openness_values
            ),
            "mouth_openness_mean": self._mean(
                mouth_openness_values
            ),
            "mouth_openness_stddev": self._std(
                mouth_openness_values
            ),
            "brow_eye_distance_mean": self._mean(
                brow_eye_distance_values
            ),
            "brow_eye_distance_stddev": self._std(
                brow_eye_distance_values
            ),
            "facial_movement_mean": self._mean(
                movement_values
            ),
            "facial_movement_stddev": self._std(
                movement_values
            ),
        }

    def _landmarks_to_array(
        self,
        face_landmarks: Any,
        frame_shape: tuple[int, ...],
    ) -> np.ndarray:
        height, width = frame_shape[:2]

        points = []

        for landmark in face_landmarks.landmark:
            points.append(
                [
                    landmark.x * width,
                    landmark.y * height,
                    landmark.z,
                ]
            )

        return np.array(
            points,
            dtype=np.float32,
        )

    def _calculate_eye_openness(
        self,
        landmarks: np.ndarray,
    ) -> float:
        left_eye_top = landmarks[159]
        left_eye_bottom = landmarks[145]

        right_eye_top = landmarks[386]
        right_eye_bottom = landmarks[374]

        left_eye_distance = np.linalg.norm(
            left_eye_top - left_eye_bottom
        )

        right_eye_distance = np.linalg.norm(
            right_eye_top - right_eye_bottom
        )

        return float(
            (left_eye_distance + right_eye_distance)
            / 2
        )

    def _calculate_mouth_openness(
        self,
        landmarks: np.ndarray,
    ) -> float:
        upper_lip = landmarks[13]
        lower_lip = landmarks[14]

        return float(
            np.linalg.norm(
                upper_lip - lower_lip
            )
        )

    def _calculate_brow_eye_distance(
        self,
        landmarks: np.ndarray,
    ) -> float:
        left_brow = landmarks[105]
        left_eye = landmarks[159]

        right_brow = landmarks[334]
        right_eye = landmarks[386]

        left_distance = np.linalg.norm(
            left_brow - left_eye
        )

        right_distance = np.linalg.norm(
            right_brow - right_eye
        )

        return float(
            (left_distance + right_distance)
            / 2
        )

    def _mean(self, values: list[float]) -> float:
        if not values:
            return 0.0

        return round(float(np.mean(values)), 6)

    def _std(self, values: list[float]) -> float:
        if not values:
            return 0.0

        return round(float(np.std(values)), 6)

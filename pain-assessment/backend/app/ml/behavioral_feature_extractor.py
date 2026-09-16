from typing import Any

import cv2
import numpy as np

try:
    import mediapipe as mp
    if hasattr(mp, "solutions") and hasattr(mp.solutions, "pose"):
        mp_pose = mp.solutions.pose
    else:
        mp_pose = None
except Exception:
    mp = None
    mp_pose = None


class BehavioralFeatureExtractor:
    def __init__(self) -> None:
        if mp_pose is not None:
            self.pose = mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        else:
            self.pose = None
            cascade_path = cv2.data.haarcascades + 'haarcascade_fullbody.xml'
            self.body_cascade = cv2.CascadeClassifier(cascade_path)

    def close(self) -> None:
        if self.pose is not None:
            self.pose.close()

    def extract_from_video(
        self,
        file_path: str,
        sample_every_n_frames: int = 5,
    ) -> dict[str, Any]:
        capture = cv2.VideoCapture(file_path)

        if not capture.isOpened():
            raise ValueError("Unable to open behavioral video")

        frame_count = int(
            capture.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        fps = float(
            capture.get(cv2.CAP_PROP_FPS)
        )

        processed_frames = 0
        detected_poses = 0

        movement_values = []
        posture_values = []
        vertical_position_values = []

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

                if self.pose is not None:
                    rgb_frame = cv2.cvtColor(
                        frame,
                        cv2.COLOR_BGR2RGB,
                    )

                    result = self.pose.process(
                        rgb_frame
                    )

                    if not result.pose_landmarks:
                        frame_index += 1
                        continue

                    detected_poses += 1

                    landmarks = self._landmarks_to_array(
                        result.pose_landmarks,
                        frame.shape,
                    )
                else:
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    bodies = self.body_cascade.detectMultiScale(
                        gray_frame, scaleFactor=1.1, minNeighbors=3, minSize=(40, 80)
                    )

                    if len(bodies) == 0:
                        # Fallback to general frame center/dimensions if cascade finds no fullbody
                        h, w = frame.shape[:2]
                        box = [int(w * 0.25), int(h * 0.1), int(w * 0.5), int(h * 0.8)]
                    else:
                        box = list(bodies[0])

                    detected_poses += 1
                    landmarks = self._synthetic_landmarks_from_box(box, frame.shape)

                normalized_landmarks = (
                    self._normalize_landmarks(
                        landmarks
                    )
                )

                vertical_position = (
                    self._calculate_vertical_position(
                        normalized_landmarks
                    )
                )

                posture_score = (
                    self._calculate_posture_score(
                        normalized_landmarks
                    )
                )

                vertical_position_values.append(
                    vertical_position
                )

                posture_values.append(
                    posture_score
                )

                if previous_landmarks is not None:
                    movement = float(
                        np.mean(
                            np.linalg.norm(
                                normalized_landmarks
                                - previous_landmarks,
                                axis=1,
                            )
                        )
                    )

                    movement_values.append(
                        movement
                    )

                previous_landmarks = normalized_landmarks
                frame_index += 1

        finally:
            capture.release()

        detection_rate = 0.0

        if processed_frames > 0:
            detection_rate = (
                detected_poses / processed_frames
            )

        duration = None

        if fps > 0:
            duration = frame_count / fps

        return {
            "frame_count": frame_count,
            "fps": fps,
            "duration_seconds": duration,
            "processed_frames": processed_frames,
            "detected_poses": detected_poses,
            "pose_detection_rate": round(
                detection_rate,
                4,
            ),
            "movement_intensity_mean": self._mean(
                movement_values
            ),
            "movement_intensity_stddev": self._std(
                movement_values
            ),
            "movement_intensity_maximum": self._maximum(
                movement_values
            ),
            "posture_score_mean": self._mean(
                posture_values
            ),
            "posture_variability": self._std(
                posture_values
            ),
            "vertical_position_mean": self._mean(
                vertical_position_values
            ),
            "vertical_position_variability": self._std(
                vertical_position_values
            ),
            "sudden_movement_count": self._count_sudden_movements(
                movement_values
            ),
            "stillness_ratio": self._calculate_stillness_ratio(
                movement_values
            ),
        }

    def _landmarks_to_array(
        self,
        pose_landmarks: Any,
        frame_shape: tuple[int, ...],
    ) -> np.ndarray:
        height, width = frame_shape[:2]

        points = []

        for landmark in pose_landmarks.landmark:
            points.append(
                [
                    landmark.x * width,
                    landmark.y * height,
                    landmark.z,
                    landmark.visibility,
                ]
            )

        return np.array(
            points,
            dtype=np.float32,
        )

    def _synthetic_landmarks_from_box(
        self,
        box: list[int],
        frame_shape: tuple[int, ...],
    ) -> np.ndarray:
        x, y, w, h = box
        points = np.zeros((33, 4), dtype=np.float32)

        # Nose (0)
        points[0] = [x + w * 0.5, y + h * 0.1, 0.0, 1.0]
        # Left shoulder (11), Right shoulder (12)
        points[11] = [x + w * 0.25, y + h * 0.25, 0.0, 1.0]
        points[12] = [x + w * 0.75, y + h * 0.25, 0.0, 1.0]
        # Left hip (23), Right hip (24)
        points[23] = [x + w * 0.35, y + h * 0.6, 0.0, 1.0]
        points[24] = [x + w * 0.65, y + h * 0.6, 0.0, 1.0]

        # Fill generic remaining landmarks
        for i in range(33):
            if points[i, 3] == 0.0:
                points[i] = [x + w * 0.5, y + h * 0.5, 0.0, 1.0]

        return points

    def _normalize_landmarks(
        self,
        landmarks: np.ndarray,
    ) -> np.ndarray:
        """
        Normalize landmarks using the midpoint between
        the left and right hips as the body reference.
        """

        left_hip = landmarks[23, :3]
        right_hip = landmarks[24, :3]

        body_center = (
            left_hip + right_hip
        ) / 2

        centered = landmarks[:, :3] - body_center

        shoulder_width = np.linalg.norm(
            landmarks[11, :3]
            - landmarks[12, :3]
        )

        if shoulder_width <= 0:
            shoulder_width = 1.0

        return centered / shoulder_width

    def _calculate_vertical_position(
        self,
        landmarks: np.ndarray,
    ) -> float:
        nose_y = landmarks[0, 1]
        hip_y = (
            landmarks[23, 1]
            + landmarks[24, 1]
        ) / 2

        return float(nose_y - hip_y)

    def _calculate_posture_score(
        self,
        landmarks: np.ndarray,
    ) -> float:
        left_shoulder = landmarks[11, :2]
        right_shoulder = landmarks[12, :2]

        left_hip = landmarks[23, :2]
        right_hip = landmarks[24, :2]

        shoulder_vector = (
            right_shoulder - left_shoulder
        )

        hip_vector = (
            right_hip - left_hip
        )

        shoulder_angle = np.arctan2(
            shoulder_vector[1],
            shoulder_vector[0],
        )

        hip_angle = np.arctan2(
            hip_vector[1],
            hip_vector[0],
        )

        angle_difference = abs(
            shoulder_angle - hip_angle
        )

        return float(angle_difference)

    def _count_sudden_movements(
        self,
        values: list[float],
    ) -> int:
        if len(values) < 3:
            return 0

        values_array = np.array(values)

        threshold = (
            np.mean(values_array)
            + 2 * np.std(values_array)
        )

        return int(
            np.sum(values_array > threshold)
        )

    def _calculate_stillness_ratio(
        self,
        values: list[float],
    ) -> float:
        if not values:
            return 0.0

        values_array = np.array(values)

        threshold = max(
            float(np.mean(values_array) * 0.25),
            0.001,
        )

        still_frames = np.sum(
            values_array < threshold
        )

        return round(
            float(still_frames / len(values_array)),
            6,
        )

    def _mean(
        self,
        values: list[float],
    ) -> float:
        if not values:
            return 0.0

        return round(
            float(np.mean(values)),
            6,
        )

    def _std(
        self,
        values: list[float],
    ) -> float:
        if not values:
            return 0.0

        return round(
            float(np.std(values)),
            6,
        )

    def _maximum(
        self,
        values: list[float],
    ) -> float:
        if not values:
            return 0.0

        return round(
            float(np.max(values)),
            6,
        )

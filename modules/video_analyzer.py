"""
Video Analysis Module using MediaPipe
Analyzes face detection, gaze tracking, and body language
"""

import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
import json


class VideoAnalyzer:
    """
    Singleton class for video analysis using MediaPipe Face Mesh
    """
    _instance = None
    _face_mesh = None
    
    def __new__(cls):
        """Singleton pattern - create only one instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize MediaPipe Face Mesh (runs once)"""
        print("🔄 Loading MediaPipe Face Mesh...")
        
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self._face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,  # For video stream
            max_num_faces=1,  # Track only one face
            refine_landmarks=True,  # Better accuracy for eyes
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmark indices (MediaPipe has 468 landmarks)
        # Left eye: 33, 133, 160, 159, 158, 157, 173, 144, 145, 153, 154, 155
        # Right eye: 362, 263, 466, 388, 387, 386, 385, 384, 398, 362, 382, 381
        self.LEFT_EYE = [33, 133, 160, 159, 158, 157, 173, 145]
        self.RIGHT_EYE = [362, 263, 466, 388, 387, 386, 385, 398]
        
        # Iris landmarks
        self.LEFT_IRIS = [468, 469, 470, 471, 472]
        self.RIGHT_IRIS = [473, 474, 475, 476, 477]
        
        print("✅ MediaPipe Face Mesh loaded!")
    
    def detect_face(self, frame):
        """
        Detect face in a single frame
        
        Args:
            frame: OpenCV image (BGR format)
        
        Returns:
            results: MediaPipe face mesh results or None
        """
        # Convert BGR to RGB (MediaPipe uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame
        results = self._face_mesh.process(rgb_frame)
        
        return results
    
    def calculate_gaze_direction(self, face_landmarks, frame_width, frame_height):
        """
        Calculate where the person is looking
        
        Args:
            face_landmarks: MediaPipe face landmarks
            frame_width: Width of frame
            frame_height: Height of frame
        
        Returns:
            dict: {
                'looking_at_camera': bool,
                'horizontal_ratio': float (-1 to 1, 0 = center),
                'vertical_ratio': float (-1 to 1, 0 = center)
            }
        """
        # Get left iris center
        left_iris_x = np.mean([face_landmarks.landmark[i].x for i in self.LEFT_IRIS])
        left_iris_y = np.mean([face_landmarks.landmark[i].y for i in self.LEFT_IRIS])
        
        # Get right iris center
        right_iris_x = np.mean([face_landmarks.landmark[i].x for i in self.RIGHT_IRIS])
        right_iris_y = np.mean([face_landmarks.landmark[i].y for i in self.RIGHT_IRIS])
        
        # Get left eye corners (to calculate eye box)
        left_eye_left = face_landmarks.landmark[33].x  # Left corner
        left_eye_right = face_landmarks.landmark[133].x  # Right corner
        
        # Calculate where iris is within the eye (0 = center, -1 = left, 1 = right)
        left_eye_width = left_eye_right - left_eye_left
        left_iris_position = (left_iris_x - left_eye_left) / left_eye_width
        horizontal_ratio = (left_iris_position - 0.5) * 2  # Normalize to -1 to 1
        
        # Vertical gaze (simplified - just using iris y position)
        vertical_ratio = (left_iris_y - 0.5) * 2
        
        # Determine if looking at camera
        # Camera = horizontal near 0, vertical near 0
        threshold = 0.3  # How close to center counts as "looking at camera"
        looking_at_camera = (
            abs(horizontal_ratio) < threshold and 
            abs(vertical_ratio) < threshold
        )
        
        return {
            'looking_at_camera': looking_at_camera,
            'horizontal_ratio': round(horizontal_ratio, 2),
            'vertical_ratio': round(vertical_ratio, 2)
        }
    
    def analyze_frame(self, frame):
        """
        Complete analysis of a single frame
        
        Args:
            frame: OpenCV image (numpy array)
        
        Returns:
            dict with analysis results or None if no face detected
        """
        if frame is None or frame.size == 0:
            return None
        
        height, width = frame.shape[:2]
        
        # Detect face
        results = self.detect_face(frame)
        
        if not results.multi_face_landmarks:
            return {
                'face_detected': False,
                'looking_at_camera': False,
                'timestamp': datetime.now().isoformat()
            }
        
        # Get first face (we only track one)
        face_landmarks = results.multi_face_landmarks[0]
        
        # Calculate gaze
        gaze = self.calculate_gaze_direction(face_landmarks, width, height)
        
        return {
            'face_detected': True,
            'looking_at_camera': gaze['looking_at_camera'],
            'horizontal_gaze': gaze['horizontal_ratio'],
            'vertical_gaze': gaze['vertical_ratio'],
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_video_frames(self, frames):
        """
        Analyze multiple frames from video recording
        
        Args:
            frames: List of OpenCV images
        
        Returns:
            dict with overall video metrics
        """
        if not frames or len(frames) == 0:
            return None
        
        total_frames = len(frames)
        frames_with_face = 0
        frames_looking_at_camera = 0
        violations = []  # Timestamps when not looking at camera
        
        # Analyze each frame
        for idx, frame in enumerate(frames):
            result = self.analyze_frame(frame)
            
            if result and result['face_detected']:
                frames_with_face += 1
                
                if result['looking_at_camera']:
                    frames_looking_at_camera += 1
                else:
                    # Record violation
                    violations.append({
                        'frame_number': idx,
                        'timestamp': result['timestamp']
                    })
        
        # Calculate scores
        face_detection_rate = (frames_with_face / total_frames) * 100 if total_frames > 0 else 0
        eye_contact_score = (frames_looking_at_camera / frames_with_face) * 100 if frames_with_face > 0 else 0
        
        return {
            'total_frames': total_frames,
            'frames_with_face': frames_with_face,
            'face_detection_rate': round(face_detection_rate, 2),
            'frames_looking_at_camera': frames_looking_at_camera,
            'eye_contact_score': round(eye_contact_score, 2),
            'gaze_violations': len(violations),
            'violation_details': violations[:10]  # Keep only first 10 for storage
        }
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self._face_mesh:
            self._face_mesh.close()


# Test function
if __name__ == "__main__":
    print("Testing Video Analyzer...")
    analyzer = VideoAnalyzer()
    print("✅ Video Analyzer initialized!")
import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Face Detection and Face Mesh
mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

class GazeDetector:
    def __init__(self):
        self.face_detector = mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
    def get_gaze_direction(self, face_landmarks, frame_shape):
        """Estimate gaze direction from face landmarks"""
        h, w = frame_shape[:2]
        
        try:
            # Key eye and face points
            left_eye_inner = face_landmarks[133]
            right_eye_inner = face_landmarks[362]
            left_eye_outer = face_landmarks[33]
            right_eye_outer = face_landmarks[263]
            
            # Nose tip
            nose_tip = face_landmarks[1]
            
            # Calculate eye centers
            left_eye_center = np.array([
                (left_eye_inner.x + left_eye_outer.x) / 2 * w,
                (left_eye_inner.y + left_eye_outer.y) / 2 * h
            ])
            
            right_eye_center = np.array([
                (right_eye_inner.x + right_eye_outer.x) / 2 * w,
                (right_eye_inner.y + right_eye_outer.y) / 2 * h
            ])
            
            # Nose position
            nose = np.array([
                nose_tip.x * w,
                nose_tip.y * h
            ])
            
            # Average eye position
            avg_eye = (left_eye_center + right_eye_center) / 2
            
            # Calculate gaze vector (where eyes point relative to nose)
            gaze_vector = avg_eye - nose
            
            # Normalize
            magnitude = np.linalg.norm(gaze_vector)
            if magnitude > 0:
                gaze_vector = gaze_vector / magnitude
            
            # Determine direction based on gaze vector
            angle = np.arctan2(gaze_vector[1], gaze_vector[0]) * 180 / np.pi
            
            """if angle > 45:
                direction = "DOWN"
            elif angle < -45:
                direction = "UP"
            elif gaze_vector[0] > 0.3:
                direction = "RIGHT"
            elif gaze_vector[0] < -0.3:
                direction = "LEFT"
            else:
                direction = "FORWARD"
                
            return direction"""
            return angle
        except:
            return "UNKNOWN"
    
    def process_frame(self, frame):
        """Process frame to detect persons and their gaze direction"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape
        
        # Detect faces using face detection
        face_results = self.face_detector.process(rgb_frame)
        faces_info = []
        
        if face_results.detections:
            for idx, detection in enumerate(face_results.detections):
                if idx >= 3:  # Limit to 3 persons
                    break
                
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Ensure bbox is within frame
                x = max(0, x)
                y = max(0, y)
                width = min(width, w - x)
                height = min(height, h - y)
                
                # Get face landmarks for gaze estimation on full frame
                mesh_results = self.face_mesh.process(rgb_frame)
                
                gaze_dir = "UNKNOWN"
                if mesh_results.multi_face_landmarks and idx < len(mesh_results.multi_face_landmarks):
                    landmarks = mesh_results.multi_face_landmarks[idx].landmark
                    gaze_dir = self.get_gaze_direction(landmarks, frame.shape)
                
                faces_info.append({
                    'id': idx + 1,
                    'bbox': (x, y, width, height),
                    'gaze': gaze_dir,
                    'confidence': detection.score[0]
                })
        
        return frame, faces_info
    
    def draw_results(self, frame, faces_info):
        """Draw bounding boxes and gaze direction on frame"""
        for face in faces_info:
            x, y, w, h = face['bbox']
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Put person ID and gaze direction
            text = f"Person {face['id']}: {face['gaze']}"
            cv2.putText(
                frame, text, (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )
            
            # Put confidence
            conf_text = f"Conf: {face['confidence']:.2f}"
            cv2.putText(
                frame, conf_text, (x, y+h+20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 1
            )
        
        return frame

def main():
    cap = cv2.VideoCapture(0)  # Use webcam
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    detector = GazeDetector()
    
    print("Starting video capture. Press 'q' to quit.")
    print("Make sure at least 3 people are visible in the camera.")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Flip frame horizontally for selfie-view
        frame = cv2.flip(frame, 1)
        
        faces_info = None
        # Process frame every 2 frames to improve performance
        if frame_count % 2 == 0:
            _, faces_info = detector.process_frame(frame)
        
        if faces_info != None:
        # Draw results
            frame = detector.draw_results(frame, faces_info)
            
            # Display information
            cv2.putText(
                frame, f"Detected: {len(faces_info)} persons",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
            )
            
            # Show frame
            cv2.imshow('Gaze Direction Detector', frame)
            
            # Print console output
            if frame_count % 30 == 0 and faces_info:
                print("\n--- Frame Info ---")
                for face in faces_info:
                    print(f"Person {face['id']}: Looking {face['gaze']} "
                        f"(Confidence: {face['confidence']:.2f})")
        
        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Done!")

if __name__ == "__main__":
    main()
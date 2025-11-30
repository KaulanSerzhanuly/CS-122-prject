"""
Webcam capture for personalized screamers.
Captures user's face, applies horror effects, and saves for the screamer pipeline.
"""

import cv2
import numpy as np
import os
import time


def apply_horror_effect(image: np.ndarray) -> np.ndarray:
    """Apply a horror visual effect to the captured image."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Increase contrast (using histogram equalization)
    equalized = cv2.equalizeHist(gray)
    
    # Add some noise
    noise = np.random.randint(0, 50, equalized.shape, dtype='uint8')
    noisy_image = cv2.add(equalized, noise)
    
    # Apply a subtle motion blur
    kernel_size = 15
    kernel_motion_blur = np.zeros((kernel_size, kernel_size))
    kernel_motion_blur[int((kernel_size-1)/2), :] = np.ones(kernel_size)
    kernel_motion_blur = kernel_motion_blur / kernel_size
    blurred = cv2.filter2D(noisy_image, -1, kernel_motion_blur)
    
    # Convert back to 3-channel BGR for pygame compatibility
    final_image = cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR)
    
    return final_image


def capture_and_save_face(asset_path: str = "assets/images/", filename: str = "user_capture.png"):
    """
    Captures an image from the webcam, detects a face, applies a horror
    effect, and saves it to the specified path.
    """
    # This file is often not included in packages, so we find its path dynamically
    cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
    if not os.path.exists(cascade_path):
        print("Could not find face detection model.")
        return

    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    # Try to open the webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam.")
        return

    # Give webcam time to initialize
    time.sleep(1) 

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to capture frame from webcam.")
        return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) > 0:
        # Use the largest face found
        (x, y, w, h) = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
        face_image = frame[y:y+h, x:x+w]
        
        # Apply horror effect
        processed_face = apply_horror_effect(face_image)
        
        # Save the processed image
        output_path = os.path.join(asset_path, filename)
        try:
            cv2.imwrite(output_path, processed_face)
            print(f"Saved user capture to {output_path}")
        except Exception as e:
            print(f"Failed to save user capture: {e}")
    else:
        print("No face detected in webcam capture.")
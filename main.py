import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet
import cv2
import face_recognition
import numpy as np
import os

# Function to generate a key and save it to a file
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    return key

# Function to load the key from a file
def load_key():
    return open("secret.key", "rb").read()

# Function to encrypt a file
def encrypt_file(file_name, key):
    fernet = Fernet(key)
    with open(file_name, "rb") as file:
        file_data = file.read()
    encrypted_data = fernet.encrypt(file_data)
    with open(file_name + ".enc", "wb") as file:
        file.write(encrypted_data)
    messagebox.showinfo("Success", f"File '{file_name}' has been encrypted successfully!")

# Function to select a file and encrypt it
def select_file():
    if verify_face():
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                key = load_key()
            except FileNotFoundError:
                key = generate_key()
            encrypt_file(file_path, key)
    else:
        messagebox.showerror("Error", "Face verification failed!")

# Function to capture a reference image of the user's face
def capture_reference_image():
    video_capture = cv2.VideoCapture(0)
    messagebox.showinfo("Info", "Please look at the camera to capture your face.")

    while True:
        ret, frame = video_capture.read()
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            # Convert the captured frame to RGB before saving
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imwrite("reference.jpg", rgb_frame)
            break

    video_capture.release()
    cv2.destroyAllWindows()

# Function to verify the user's face
def verify_face():
    if not os.path.exists("reference.jpg"):
        capture_reference_image()
        messagebox.showinfo("Info", "Reference image captured. Please try encrypting the file again.")
        return False

    # Load the reference image using OpenCV
    reference_image = cv2.imread("reference.jpg")
    if reference_image is None:
        messagebox.showerror("Error", "Could not load reference image.")
        return False

    # Ensure the image is in RGB format
    if reference_image.shape[2] == 4:  # Check for RGBA
        reference_image = cv2.cvtColor(reference_image, cv2.COLOR_RGBA2RGB)
    elif reference_image.shape[2] == 1:  # Check for grayscale
        reference_image = cv2.cvtColor(reference_image, cv2.COLOR_GRAY2RGB)
    elif reference_image.shape[2] != 3:
        messagebox.showerror("Error", "Reference image is not in a valid format.")
        return False
    
    # Debugging information
    print(f"Image shape: {reference_image.shape}")
    print(f"Image dtype: {reference_image.dtype}")

    # Ensure the image is 8-bit per channel
    if reference_image.dtype != np.uint8:
        messagebox.showerror("Error", "Reference image is not 8-bit per channel.")
        return False

    # Ensure the image is RGB
    if reference_image.shape[2] != 3:
        messagebox.showerror("Error", "Reference image is not RGB.")
        return False

    # Further debugging steps
    print(f"Reference image array:\n{reference_image}")

    try:
        # Check for face locations
        face_locations = face_recognition.face_locations(reference_image)
        if len(face_locations) == 0:
            messagebox.showerror("Error", "No face found in the reference image.")
            return False
        
        # Get face encodings
        reference_encoding = face_recognition.face_encodings(reference_image, known_face_locations=face_locations)
        if len(reference_encoding) == 0:
            messagebox.showerror("Error", "Failed to encode face in the reference image.")
            return False
        
        reference_encoding = reference_encoding[0]
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during face encoding: {str(e)}")
        return False
    
    video_capture = cv2.VideoCapture(0)
    messagebox.showinfo("Info", "Please look at the camera for face verification.")

    while True:
        ret, frame = video_capture.read()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces([reference_encoding], face_encoding)
            if True in matches:
                video_capture.release()
                cv2.destroyAllWindows()
                return True

        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return False

# Create the main window
root = tk.Tk()
root.title("File Encryptor")

# Create and place widgets
label = tk.Label(root, text="Select a file to encrypt:")
label.pack(pady=10)

select_button = tk.Button(root, text="Select File", command=select_file)
select_button.pack(pady=10)

# Run the main loop
root.mainloop()
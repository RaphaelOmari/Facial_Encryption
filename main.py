import threading
import cv2
from deepface import DeepFace
from cryptography.fernet import Fernet

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
counter = 0

reference_img = cv2.imread("reference.jpg")

face_match = False
lock = threading.Lock()

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

def check_face(frame):
    global face_match
    try:
        result = DeepFace.verify(frame, reference_img.copy())["verified"]
        with lock:
            face_match = result
    except Exception as e:
        with lock:
            face_match = False
        print(e)

# Generate and save a key if not already done
try:
    key = load_key()
except FileNotFoundError:
    key = generate_key()

while True:
    ret, frame = cap.read()

    if ret:
        if counter % 30 == 0:
            try:
                threading.Thread(target=check_face, args=(frame.copy(),)).start()
            except Exception as e:
                print(e)

        counter += 1

        with lock:
            if face_match:
                cv2.putText(frame, "MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            else:
                cv2.putText(frame, "NO MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

        cv2.imshow("video", frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Example usage: encrypt a file named "example.txt"
encrypt_file("example.txt", key)
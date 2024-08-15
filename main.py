import cv2
import numpy as np
import os
from tkinter import Tk, Button, Label
from PIL import Image, ImageTk

# Initialize variables
clothing_images = []
selected_cloth = None

# Load clothing images
clothes_folder = 'clothes'
for filename in os.listdir(clothes_folder):
    if filename.endswith('.png'):
        img = cv2.imread(os.path.join(clothes_folder, filename), -1)
        clothing_images.append(img)

def overlay_cloth(frame, cloth_img):
    """Overlay the selected clothing on the video frame."""
    cloth_h, cloth_w, _ = cloth_img.shape
    frame_h, frame_w, _ = frame.shape

    # Resize the clothing image to fit within the frame
    scale_factor = min(frame_w / cloth_w, frame_h / cloth_h)
    new_cloth_w = int(cloth_w * scale_factor)
    new_cloth_h = int(cloth_h * scale_factor)

    cloth_img_resized = cv2.resize(cloth_img, (new_cloth_w, new_cloth_h), interpolation=cv2.INTER_AREA)

    # Positioning the cloth (centered horizontally, 1/4th from the top)
    top_left_y = int(frame_h / 4)
    top_left_x = int((frame_w - new_cloth_w) / 2)

    # Make sure the cloth image doesn't go out of the frame bounds
    if top_left_y + new_cloth_h > frame_h:
        new_cloth_h = frame_h - top_left_y
        cloth_img_resized = cloth_img_resized[:new_cloth_h, :, :]

    if top_left_x + new_cloth_w > frame_w:
        new_cloth_w = frame_w - top_left_x
        cloth_img_resized = cloth_img_resized[:, :new_cloth_w, :]

    # Overlay clothing image with alpha blending
    alpha_s = cloth_img_resized[:, :, 3] / 255.0
    alpha_l = 1.0 - alpha_s

    for c in range(0, 3):
        frame[top_left_y:top_left_y + new_cloth_h, top_left_x:top_left_x + new_cloth_w, c] = (
            alpha_s * cloth_img_resized[:, :, c] +
            alpha_l * frame[top_left_y:top_left_y + new_cloth_h, top_left_x:top_left_x + new_cloth_w, c]
        )

    return frame

def select_cloth(index):
    global selected_cloth
    selected_cloth = clothing_images[index]

def update_frame(label, cap):
    ret, frame = cap.read()
    if not ret:
        return

    # Resize the frame for better visibility
    frame = cv2.resize(frame, (640, 480))  # Adjust the size as needed

    if selected_cloth is not None:
        frame = overlay_cloth(frame, selected_cloth)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)

    label.imgtk = imgtk  # Keep a reference to avoid garbage collection
    label.config(image=imgtk)

    label.after(10, update_frame, label, cap)

def start_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    camera_label = Label(root)
    camera_label.grid(row=2, columnspan=10)

    update_frame(camera_label, cap)

# Set up Tkinter window
root = Tk()
root.title('Virtual Cloth Trial Room')

# Add buttons for each clothing item
for i, cloth_img in enumerate(clothing_images):
    img = Image.fromarray(cv2.cvtColor(cloth_img, cv2.COLOR_BGRA2RGBA))
    img.thumbnail((100, 100))
    img = ImageTk.PhotoImage(img)

    button = Button(root, image=img, command=lambda i=i: select_cloth(i))
    button.image = img  # Keep a reference to avoid garbage collection
    button.grid(row=0, column=i)

start_button = Button(root, text="Start Camera", command=start_camera)
start_button.grid(row=1, columnspan=10)

root.mainloop()

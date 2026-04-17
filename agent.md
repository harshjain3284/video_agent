# Automated Image-to-Video Generation Agent (Open-Source)

## **Overview**

This project automates the generation of short video clips (5-6 seconds) from user-provided input text. The system works as an **automated agent** that will:
1. Parse the input text.
2. Generate images based on scene descriptions.
3. Apply motion effects to the images.
4. Stitch the images together to create a final video output (20–30 seconds).
5. Perform the entire process automatically, from input to video creation.

### **Objective**
- Automate the generation of short video clips from text input using **open-source** tools for image and motion generation.
- **End Goal**: The system should take an input (a text description), generate a video (5–6 second motion clip per scene), and combine them into a final 20–30 second video.

---

## **Project Workflow**

### **1. Input Parsing (Text Breakdown)**
- **Input**: A text prompt (e.g., "You got an income tax notice this morning. Here is the first thing you must do and the one thing you must never do.").
- **Objective**: Break down the text into actionable scenes and script descriptions.
- **Open-Source Tool**: Use **GPT-Neo** or **GPT-J** for natural language processing tasks. These models are open-source and can be run locally.
  
#### **Example**:
For input: 
> "You got an income tax notice this morning. Here is the first thing you must do and the one thing you must never do."

The output could be:
- **Scene 1**: "An income tax notice is on a desk. A person looks at it, worried."
- **Scene 2**: "A person should never ignore the notice. They should contact an expert immediately."

---

### **2. Image Generation**
- **Objective**: Generate images for each scene.
- **Open-Source Tools**:
  - **Stable Diffusion**: A powerful model for generating images based on text prompts. You can set up and run **Stable Diffusion** locally.
  - **DALL·E Mini** (also known as **Craiyon**): Another open-source alternative that generates images from text prompts.
  
#### **Example**:
- Scene 1 Prompt: "An income tax notice on a desk. A person looks at it with a worried expression."
- Scene 2 Prompt: "A person making a phone call in urgency, to a tax expert."

---

### **3. Motion Generation**
- **Objective**: Apply basic motion effects to the generated images (zoom, pan, fade).
- **Open-Source Tools**:
  - **MoviePy**: A Python library that allows you to add motion effects (like zooming, panning, etc.) to images and videos. This tool is great for basic motion effects.
  - **OpenCV**: A library that provides advanced computer vision tools, including image manipulation and motion effects such as panning, zooming, and rotating images.

#### **Example**:
For Scene 1: Apply a slow zoom-in on the image of the tax notice.
For Scene 2: Apply a slow pan to show the person making the phone call.

```python
import cv2
import numpy as np

# Apply pan effect (move view across image)
img = cv2.imread("scene1.jpg")
height, width, _ = img.shape
window_size = (400, 300)

for i in range(0, width - window_size[0], 10):
    pan_img = img[:, i:i + window_size[0]]
    cv2.imshow("Pan", pan_img)
    cv2.waitKey(30)  # Frame delay for animation
cv2.destroyAllWindows()
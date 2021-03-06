import time
import tkinter as tk

from PIL import Image, ImageTk
import cv2

running = True
paused = False

feeds = [
    "camera_rgb",
    "camera_hsv",
    "mask_border",
    "mask_border_contours",
    "camera_border_contours",
    "camera_border_approx",
    "camera_ref_transform",
    "reference_squares",
    "camera_all_markers",
    "overhead_plot",
    "smooth_plot"
]

currentImg = None


def init():
    global root, leftFeedName, rightFeedName, leftFeedImage, rightFeedImage
    root = tk.Tk()

    leftFeedImage = tk.Label(root)
    rightFeedImage = tk.Label(root)

    leftFeedName = tk.StringVar()
    rightFeedName = tk.StringVar()

    leftFeedName.set("camera_rgb")
    rightFeedName.set("camera_all_markers")

    leftFeedMenu = tk.OptionMenu(root, leftFeedName, *feeds)
    rightFeedMenu = tk.OptionMenu(root, rightFeedName, *feeds)

    leftNextButton = tk.Button(root, text="Next", command=nextfeedleft)
    rightNextButton = tk.Button(root, text="Next", command=nextfeedleft)

    saveButton = tk.Button(root, text="Save", command=save_callback)
    pauseButton = tk.Button(root, text="Pause", command=pause_callback)

    leftFeedImage.grid(row=0, column=0, columnspan=3)
    rightFeedImage.grid(row=0, column=3, columnspan=3)
    leftFeedMenu.grid(row=1, column=0)
    leftNextButton.grid(row=1, column=1)
    saveButton.grid(row=1, column=2)
    pauseButton.grid(row=1, column=3)
    rightFeedMenu.grid(row=1, column=4)
    rightNextButton.grid(row=1, column=5)


def update():
    global root
    root.update()


def show(np_img, name):
    global leftFeedName, rightFeedName, leftFeedImage, rightFeedImage, \
        currentImg
    if name == leftFeedName.get():
        pil_img = Image.fromarray(np_img)
        tk_img = ImageTk.PhotoImage(image=pil_img)
        leftFeedImage.imgtk = tk_img
        leftFeedImage.configure(image=tk_img)

        currentImg = np_img
    if name == rightFeedName.get():
        pil_img = Image.fromarray(np_img)
        tk_img = ImageTk.PhotoImage(image=pil_img)
        rightFeedImage.imgtk = tk_img
        rightFeedImage.configure(image=tk_img)


def save_callback():
    global currentImg
    timestamp = int(time.time())
    currentImgRgb = cv2.cvtColor(currentImg, cv2.COLOR_BGR2RGB)
    cv2.imwrite(f"screenshots/lps-screenshot-{timestamp}.png",
                currentImgRgb)


def pause_callback():
    global paused
    paused = not paused


def nextfeedleft():
    global feeds, leftFeedName
    i = feeds.index(leftFeedName.get())
    leftFeedName.set(feeds[(i+1) % len(feeds)])


def nextfeedright():
    global feeds, rightFeedName
    i = feeds.index(rightFeedName.get())
    rightFeedName.set(feeds[(i+1) % len(feeds)])

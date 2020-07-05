import tkinter as tk
from PIL import Image, ImageTk

running = True

feeds = [
    "camera_rgb",
    "camera_hsv",
    "mask_border",
    "mask_border_contours",
    "camera_border_contours",
    "camera_border_approx",
    "camera_ref_transform",
    "camera_sq0",
    "camera_mask_sq0",
    "camera_gray_sq0",
    "camera_all_markers",
    "overhead_plot",
    "smooth_plot"
]


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
    quitButton = tk.Button(root, text="Quit", command=quit_callback)

    leftFeedImage.grid(row=0, column=0, columnspan=3)
    rightFeedImage.grid(row=0, column=3, columnspan=3)
    leftFeedMenu.grid(row=1, column=0)
    leftNextButton.grid(row=1, column=1)
    quitButton.grid(row=1, column=2, columnspan=2)
    rightFeedMenu.grid(row=1, column=4)
    rightNextButton.grid(row=1, column=5)


def update():
    global root
    root.update()


def show(np_img, name):
    global leftFeedName, rightFeedName, leftFeedImage, rightFeedImage
    if name == leftFeedName.get():
        pil_img = Image.fromarray(np_img)
        tk_img = ImageTk.PhotoImage(image=pil_img)
        leftFeedImage.imgtk = tk_img
        leftFeedImage.configure(image=tk_img)
    if name == rightFeedName.get():
        pil_img = Image.fromarray(np_img)
        tk_img = ImageTk.PhotoImage(image=pil_img)
        rightFeedImage.imgtk = tk_img
        rightFeedImage.configure(image=tk_img)


def quit_callback():
    global running
    running = False


def nextfeedleft():
    global feeds, leftFeedName
    i = feeds.index(leftFeedName.get())
    leftFeedName.set(feeds[(i+1) % len(feeds)])


def nextfeedright():
    global feeds, rightFeedName
    i = feeds.index(rightFeedName.get())
    rightFeedName.set(feeds[(i+1) % len(feeds)])

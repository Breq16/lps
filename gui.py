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
    "camera_lab_sq0",
    "camera_all_markers",
    "overhead_plot"
]


def init():
    global root, feedImage, feedName, feedMenu, feeds, running
    root = tk.Tk()

    feedImage = tk.Label(root)

    feedName = tk.StringVar()
    feedName.set("camera_rgb")
    feedMenu = tk.OptionMenu(root, feedName, *feeds)

    nextButton = tk.Button(root, text="Next", command=nextfeed)
    quitButton = tk.Button(root, text="Quit", command=quit_callback)

    feedImage.pack()
    feedMenu.pack()
    nextButton.pack()
    quitButton.pack()


def update():
    global root
    root.update()


def show(np_img, name):
    global feedName
    if name == feedName.get():
        pil_img = Image.fromarray(np_img)
        tk_img = ImageTk.PhotoImage(image=pil_img)
        feedImage.imgtk = tk_img
        feedImage.configure(image=tk_img)


def quit_callback():
    global running
    running = False


def nextfeed():
    global feeds, feedName
    i = feeds.index(feedName.get())
    feedName.set(feeds[(i+1) % len(feeds)])

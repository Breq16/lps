import tkinter as tk
from PIL import Image, ImageTk

import numpy as np
import cv2


root = tk.Tk()

cameraLabel = tk.Label(root)
maskLabel = tk.Label(root)

cameraLabel.grid(row=0, column=0, columnspan=3)
maskLabel.grid(row=0, column=3, columnspan=3)


class lowHighSel(tk.Frame):
    def __init__(self, root, name, low=0, high=0):
        tk.Frame.__init__(self, root)

        self.lowvar = tk.StringVar()
        self.highvar = tk.StringVar()

        self.low = low
        self.high = high

        self.lowvar.set(str(self.low))
        self.highvar.set(str(self.high))

        tk.Label(self, text=name).grid(row=0, column=0)
        tk.Entry(self, textvariable=self.lowvar).grid(row=0, column=1)
        tk.Entry(self, textvariable=self.highvar).grid(row=0, column=2)
        tk.Button(self, text="set", command=self.update).grid(row=0, column=3)

    def update(self):
        try:
            self.low = int(self.lowvar.get())
            self.high = int(self.highvar.get())
        except ValueError:
            pass


hueSel = lowHighSel(root, "Hue")
satSel = lowHighSel(root, "Sat")
valSel = lowHighSel(root, "Val")

hueSel.grid(row=1, column=0, columnspan=2)
satSel.grid(row=1, column=2, columnspan=2)
valSel.grid(row=1, column=4, columnspan=2)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 15)

while True:
    root.update()

    _, image = cap.read()

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    pil_image_rgb = Image.fromarray(image_rgb)
    tk_image_rgb = ImageTk.PhotoImage(image=pil_image_rgb)
    cameraLabel.imgtk = tk_image_rgb
    cameraLabel.configure(image=tk_image_rgb)

    MASK_LOW = np.array([hueSel.low, satSel.low, valSel.low])
    MASK_HIGH = np.array([hueSel.high, satSel.high, valSel.high])

    image_mask = cv2.inRange(image_hsv, MASK_LOW, MASK_HIGH)

    pil_image_mask = Image.fromarray(image_mask)
    tk_image_mask = ImageTk.PhotoImage(image=pil_image_mask)
    maskLabel.imgtk = tk_image_mask
    maskLabel.configure(image=tk_image_mask)

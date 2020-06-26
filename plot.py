import numpy as np
import cv2

plot_img = np.zeros((500, 500, 3), np.uint8)

marker_colors = {
    "reference": (255, 0, 255),
    "target": (0, 255, 255),
    "label": (255, 255, 0),
    "none": (0, 0, 255)
}


def clear():
    global plot_img
    plot_img = np.zeros((500, 500, 3), np.uint8)


def coord_to_pixel(pos):
    global plot_img
    x = plot_img.shape[1]/2 + pos[0]*20 + 10
    y = plot_img.shape[1]/2 - pos[1]*20 - 10
    return (int(round(x)), int(round(y)))


def plot(marker):
    global plot_img, marker_colors
    global_pos = marker.global_pos()
    if global_pos is None:
        return

    cv2.circle(plot_img, coord_to_pixel(global_pos),
               10, marker_colors[marker.type], 2)

    if marker.num >= 0:
        cv2.putText(plot_img, str(marker.num), coord_to_pixel(global_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0, 0), 3)


def show():
    global plot_img

    cv2.imshow("Plot", plot_img)

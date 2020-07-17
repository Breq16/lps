import sys

import cv2
import numpy as np

import scanner
import plot
import gui
import server
import smooth

cap = cv2.VideoCapture(int(sys.argv[1]))
cap.set(cv2.CAP_PROP_FPS, 15)

gui.init()
server.start()

while True:
    gui.update()
    if gui.paused:
        continue

    _, image = cap.read()
    plot.clear()

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gui.show(image_rgb, "camera_rgb")

    image_marker_view = image_rgb.copy()

    markers = scanner.scan(image)

    reference = None
    for marker in markers:
        if marker.type == "reference":
            reference = marker
            break

    for marker in markers:
        marker.use_reference(reference)
        marker.display(image_marker_view)
        plot.plot(marker)
        smooth.register(marker)

    gui.show(image_marker_view, "camera_all_markers")
    gui.show(plot.plot_img, "overhead_plot")

    image_ref_transform = image_rgb.copy()
    if reference is not None:
        reference.display(image_ref_transform)
    gui.show(image_ref_transform, "camera_ref_transform")

    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image_squares = cv2.cvtColor(image_gray, cv2.COLOR_GRAY2RGB)

    if reference is not None:
        for row in range(2):
            for col in range(2):
                boundary_points = ((col, row), (col-1, row),
                                   (col-1, row-1), (col, row-1))
                picture_points = np.array(tuple(reference.pic_pos(point)
                                                for point in boundary_points),
                                          np.intc)
                cv2.polylines(image_squares, [picture_points],
                              True, (255, 255, 0), 2)

        cv2.rectangle(image_squares, (10, 200), (60, 250),
                      3*(reference.min,), -1)
        cv2.rectangle(image_squares, (80, 200), (130, 250),
                      3*(reference.max,), -1)
        cv2.putText(image_squares, str(reference.squares), (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0, 0), 3)
    gui.show(image_squares, "reference_squares")

    smooth.prune()
    gui.show(smooth.render(), "smooth_plot")

    server.send_json(smooth.dump())

    server.accept_clients()

    if not gui.running:
        break

cap.release()
server.close()

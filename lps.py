import cv2
import numpy as np

import scanner
import plot
import gui
import server

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 15)

gui.init()
server.start()

while True:
    server.accept_clients()

    _, image = cap.read()
    plot.clear()

    state = []

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gui.show(image_rgb, "camera_rgb")

    image_marker_view = image_rgb.copy()

    markers = scanner.scan(image)
    for marker in markers:
        marker.scan(image)

    reference = None
    for marker in markers:
        if marker.type == "reference":
            reference = marker
            break

    for marker in markers:
        marker.use_reference(reference)
        marker.display(image_marker_view)
        plot.plot(marker)
        state.append({
            "type": marker.type,
            "pos": marker.global_pos((0, 0)),
            "front": marker.global_pos((0, 4)),
            "num": marker.num
        })

    gui.show(image_marker_view, "camera_all_markers")
    gui.show(plot.plot_img, "overhead_plot")

    image_ref_transform = image_rgb.copy()
    if reference is not None:
        reference.display(image_ref_transform)
    gui.show(image_ref_transform, "camera_ref_transform")

    image_ref_sq_zero = image_rgb.copy()
    mask_ref_sq_zero = np.zeros((image_rgb.shape[0], image_rgb.shape[1], 1),
                                np.uint8)
    if reference is not None:
        boundary_points = ((1, 1), (0, 1), (0, 0), (1, 0))
        picture_points = np.array(tuple(reference.pic_pos(point)
                                        for point in boundary_points), np.intc)
        cv2.polylines(image_ref_sq_zero, [picture_points],
                      True, (255, 255, 0), 2)
        cv2.fillPoly(mask_ref_sq_zero, [picture_points], 255)

    gui.show(image_ref_sq_zero, "camera_sq0")
    gui.show(cv2.bitwise_and(image_rgb, image_rgb, mask=mask_ref_sq_zero),
             "camera_mask_sq0")

    image_lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    image_lab_sq0 = cv2.bitwise_and(image_lab, image_lab,
                                    mask=mask_ref_sq_zero)

    cv2.rectangle(image_lab_sq0, (10, 200), (60, 250), (182, 76, 196), -1)
    cv2.rectangle(image_lab_sq0, (80, 200), (130, 250), (164, 187, 151), -1)

    if reference is not None:
        cv2.putText(image_lab_sq0, reference.squares[0], (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0, 0), 3)
    gui.show(image_lab_sq0, "camera_lab_sq0")

    gui.update()

    server.send_json(state)

    if not gui.running:
        break

cap.release()
server.close()

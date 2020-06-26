import cv2

import scanner

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 15)


while True:
    _, image = cap.read()

    markers = scanner.scan(image)
    for marker in markers:
        marker.scan(image)

    reference = None
    for marker in markers:
        if marker.type == "reference":
            reference = marker
            break

    for marker in markers:
        if reference is not None:
            global_pos = reference.scene_pos_marker(marker, False)
        else:
            global_pos = "NO REF"

        marker.display(image)
        cv2.putText(image, f"{global_pos}:{marker.squares}", marker.pic_pos(),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255, 0), 3)

    cv2.imshow("Frame", image)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

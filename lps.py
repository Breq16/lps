import cv2

import scanner
import plot

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 15)


while True:
    _, image = cap.read()
    plot.clear()

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

        marker.display(image)
        plot.plot(marker)

    cv2.imshow("Frame", image)
    plot.show()

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

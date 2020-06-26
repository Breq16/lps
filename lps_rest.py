import threading

import cv2
from flask import Flask, jsonify

import lps

app = Flask(__name__)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 15)


@app.route("/markers")
def markers():
    retobj = []
    for marker in lps.markers:
        markerjson = {"type": marker.type}
        if lps.reference is not None:
            markerjson["pos"] = lps.reference.scene_pos_marker(marker, False)
        else:
            markerjson["pos"] = (0, 0)
        if marker.type == "label":
            markerjson["label"] = marker.aux_squares
        retobj.append(markerjson)
    return jsonify(retobj)


threading.Thread(target=app.run).start()

try:
    while True:
        _, image = cap.read()
        lps.update(image)
finally:
    cap.release()

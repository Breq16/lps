import scanner

reference = None
markers = []


def update(image):
    global markers, reference

    new_markers = scanner.scan(image)
    for marker in new_markers:
        marker.scan(image)

    new_reference = None
    for marker in new_markers:
        if marker.type == "reference":
            new_reference = marker
            break

    markers = new_markers
    reference = new_reference

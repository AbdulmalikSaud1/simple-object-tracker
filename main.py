import cv2


def improve_brightness(frame):
    return cv2.convertScaleAbs(frame, alpha=1.6, beta=35)


def open_camera():
    if hasattr(cv2, "CAP_AVFOUNDATION"):
        cam = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
        if cam.isOpened():
            cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            return cam
        cam.release()

    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return cam


def create_tracker():
    if hasattr(cv2, "TrackerCSRT_create"):
        return cv2.TrackerCSRT_create(), "CSRT"

    if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerCSRT_create"):
        return cv2.legacy.TrackerCSRT_create(), "CSRT"

    if hasattr(cv2, "TrackerKCF_create"):
        return cv2.TrackerKCF_create(), "KCF"

    if hasattr(cv2, "legacy") and hasattr(cv2.legacy, "TrackerKCF_create"):
        return cv2.legacy.TrackerKCF_create(), "KCF"

    raise RuntimeError(
        "No CSRT or KCF tracker found. Install opencv-contrib-python from requirements.txt."
    )


def get_start_frame(cam):
    print("Wait a bit, then press s.")
    print("Press q to quit.")

    # Let the camera adjust first
    for _ in range(30):
        cam.read()

    while True:
        frame_ok, frame = cam.read()
        if not frame_ok:
            return None

        frame = cv2.flip(frame, 1)
        frame = improve_brightness(frame)

        preview = frame.copy()
        cv2.putText(
            preview,
            "Press s to start",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            preview,
            "Press q to quit",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        cv2.imshow("Preview", preview)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            cv2.destroyWindow("Preview")
            return frame

        if key == ord("q"):
            cv2.destroyAllWindows()
            return None


def select_object(frame):
    while True:
        print("Draw a tight box around the object, then press ENTER or SPACE.")

        box = cv2.selectROI("Select Object", frame, fromCenter=False, showCrosshair=True)
        cv2.destroyWindow("Select Object")

        if box[2] > 0 and box[3] > 0:
            return box

        print("Please try again.")


def smooth_box(old_box, new_box):
    x1, y1, w1, h1 = old_box
    x2, y2, w2, h2 = new_box

    x = int(0.7 * x1 + 0.3 * x2)
    y = int(0.7 * y1 + 0.3 * y2)
    w = int(0.7 * w1 + 0.3 * w2)
    h = int(0.7 * h1 + 0.3 * h2)

    return (x, y, w, h)


def main():
    cam = open_camera()

    if not cam.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Camera started.")
    print("Press s when the image looks okay.")
    print("Then draw a box around the object.")
    print("Press q to quit.")

    # Get a good frame first
    frame = get_start_frame(cam)
    if frame is None:
        print("Error: Could not read from webcam.")
        cam.release()
        return

    box = select_object(frame)

    try:
        tracker, tracker_name = create_tracker()
    except RuntimeError as error:
        print(error)
        cam.release()
        cv2.destroyAllWindows()
        return

    tracker.init(frame, box)
    print(f"{tracker_name} tracker started.")
    last_box = tuple(int(value) for value in box)

    while True:
        ok, frame = cam.read()
        if not ok:
            print("Error: Could not read from webcam.")
            break

        frame = cv2.flip(frame, 1)
        frame = improve_brightness(frame)

        # Update the tracker
        found, new_box = tracker.update(frame)

        if found:
            current_box = tuple(int(value) for value in new_box)
            last_box = smooth_box(last_box, current_box)
            x, y, w, h = last_box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"Tracking with {tracker_name}",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
        else:
            cv2.putText(
                frame,
                "Tracking failed",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )

        cv2.imshow("Tracker", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("Quitting...")
            break

    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

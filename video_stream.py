import imutils
import cv2
import datetime
import time

from threading import Lock

from imutils.video import VideoStream


output_frame, lock = None, Lock()
vs = VideoStream(0).start()
time.sleep(2)


def make_photo():
    global vs, output_frame, lock
    total = 0
    # loop over frames from the video stream
    while True:
        # read the next frame from the video stream, resize it,
        # convert the frame to grayscale, and blur it
        frame = vs.read()
        frame = imutils.resize(frame, width=400)
        # grab the current timestamp and draw it on the frame
        timestamp = datetime.datetime.now()
        cv2.putText(frame, timestamp.strftime(
            "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        total += 1
        # acquire the lock, set the output frame, and release the
        # lock
        with lock:
            output_frame = frame.copy()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print('break')
            break


def generate():
    # grab global references to the output frame and lock variables
    global vs, output_frame, lock
    # loop over frames from the output stream

    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if output_frame is None:
                continue
            # encode the frame in JPEG format
            flag, encoded_image = cv2.imencode(".jpg", output_frame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_image) + b'\r\n'

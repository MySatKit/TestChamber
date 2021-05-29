import cv2
import threading
import time
import datetime
import imutils

from imutils.video import VideoStream

from fastapi import FastAPI, Request
from uvicorn import run
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from os import environ, pipe, times
from typing import Dict, Any


outputFrame, lock = None, threading.Lock()
vs = VideoStream(0).start()
time.sleep(2)


app = FastAPI()
app.mount('/js', StaticFiles(directory="gui/js"), name="js")
templates = Jinja2Templates(directory="gui/html")

if not environ.get('no_rpi', False):
    from my_i2c import MyI2CBus
    from bme280 import read_BME280_all
    from bme280 import DEVICE_ADDR as bme280_addr
    from ms5611 import MS5611_ADDRESS, read_MS5611_all

    my_i2c_bus = MyI2CBus(1)
    my_i2c_bus["inside"] = bme280_addr
    my_i2c_bus["outside"] = MS5611_ADDRESS
    dummy = False
else:
    dummy = True


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("root.html", {"request": request})


class UpdateResponse(BaseModel):
    inside: Dict[str, Any]
    outside: Dict[str, Any]


def make_photo():
    global vs, outputFrame, lock
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
            outputFrame = frame.copy()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print('break')
            break


def generate():
    # grab global references to the output frame and lock variables
    global vs, outputFrame, lock
    # loop over frames from the output stream

    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
            # encode the frame in JPEG format
            flag, encodedImage = cv2.imencode(".jpg", outputFrame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')


@app.get("/video")
async def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    # return StreamingResponse(generate())
    return StreamingResponse(generate(),
                             media_type="multipart/x-mixed-replace;boundary=frame"
                             )


@app.get("/update", response_model=UpdateResponse)
async def update():
    data = {}
    if not dummy:
        t, p, h = read_BME280_all(my_i2c_bus, addr=my_i2c_bus['inside'])
        data['inside'] = {
            'temperature': t,
            'pressure': round(p, 2),
            'humidity': round(h, 2)
        }

        p, t = read_MS5611_all(my_i2c_bus, addr=my_i2c_bus['outside'])
        data['outside'] = {
            'temperature': round(t, 2),
            'pressure': round(p, 2),
        }
    else:
        data['inside'] = {
            'temperature': -40,
            'pressure': 560,
            'humidity': 2
        }
        data['outside'] = {
            'temperature': 26,
            'pressure': 1008,
            'humidity': 55
        }
    return data


if __name__ == '__main__':
    t = threading.Thread(target=make_photo)
    t.daemon = True
    t.start()

    run(app=app, port=8888)

vs.stop()

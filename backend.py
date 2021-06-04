import threading

from fastapi import FastAPI, Request
from uvicorn import run
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from os import environ
from typing import Dict, Any

from video_stream import make_photo, generate, vs


app = FastAPI()
app.mount('/js', StaticFiles(directory="gui/js"), name="js")
templates = Jinja2Templates(directory="gui/html")

if not environ.get('no_rpi', False):
    from spidev import SpiDev
    
    from my_i2c import MyI2CBus
    from bme280 import BME280
    from ms5611 import MS5611
    from my_gpio import MyRelay
    from max6675 import read_celsius

    # I2C config section -------------------------------------
    my_i2c_bus = MyI2CBus(1)
    my_i2c_bus["inside"] = BME280(my_i2c_bus)
    # my_i2c_bus["outside"] = MS5611(my_i2c_bus)
    # --------------------------------------------------------

    # SPI config section -------------------------------------
    bus_num = 0  # RPI 4 has only 1 bus_num with number 0
    device = 0  # max6675 starts transmit on CS = 0
    spi = SpiDev()
    spi.open(bus_num, device)
    spi.max_speed_hz = 300000
    spi.mode = 0
    # --------------------------------------------------------

    # GPIO config section
    my_relays = MyRelay()
    # --------------------------------------------------------

    dummy = False
else:
    dummy = True


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("root.html", {"request": request, "ln2_state": my_relays.states["liquid_nitrogen_relay"]})


class UpdateResponse(BaseModel):
    inside: Dict[str, Any]
    outside: Dict[str, Any]
    thermocouple: float


@app.get("/video", response_class=StreamingResponse)
async def video_feed():
    # return the response generated along with the specific media
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace;boundary=frame")


@app.get("/buttons/toggleLN2")
async def toggleNL2():
    state = my_relays.toggle_output("liquid_nitrogen_relay")
    return {"state": state}


@app.get("/update", response_model=UpdateResponse)
async def update():
    data = {}
    if not dummy:
        t, p, h = my_i2c_bus['inside'].read_all()
        data['inside'] = {
            'temperature': t,
            'pressure': round(p, 2),
            'humidity': round(h, 2)
        }

        # p, t = my_i2c_bus['outside'].read_all()
        data['outside'] = {
            'temperature': round(t, 2),
            'pressure': round(p, 2),
        }

        data['thermocouple'] = read_celsius(spi)
    else:
        data['inside'] = {
            'temperature': -40,
            'pressure': 560,
            'humidity': 2
        }
        data['outside'] = {
            'temperature': 26,
            'pressure': 1008
        }
        data['thermocouple'] = 55
    return data


if __name__ == '__main__':
    video_t = threading.Thread(target=make_photo)
    video_t.daemon = True
    video_t.start()

    run(app=app, port=8888)

vs.stop()
if not dummy:
    del my_relays

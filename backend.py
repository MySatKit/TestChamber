from fastapi import FastAPI, Request
from uvicorn import run
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from os import environ
from typing import Dict, Any


app = FastAPI()
app.mount('/js', StaticFiles(directory="gui/js"), name="js")
templates = Jinja2Templates(directory="gui/html")

if not environ.get('no_rpi', False):
    from my_i2c import MyI2CBus
    from bme280 import read_BME280_all, DEVICE_0, DEVICE_1

    my_i2c_bus = MyI2CBus(1)
    my_i2c_bus["inside"] = DEVICE_0
    my_i2c_bus["outside"] = DEVICE_1
    dummy = False
else:
    dummy = True


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("root.html", {"request": request})


class UpdateResponse(BaseModel):
    inside: Dict[str, Any]
    outside: Dict[str, Any]


@app.get("/update", response_model=UpdateResponse)
async def update():
    data = {}
    if not dummy:
        t, p, h = read_BME280_all(my_i2c_bus, addr=my_i2c_bus['inside'])
        data['inside'] = {
            'temperature': t,
            'pressure': p,
            'humidity': h
        }

        t, p, h = read_BME280_all(my_i2c_bus, addr=my_i2c_bus['inside'])
        data['outside'] = {
            'temperature': t,
            'pressure': p,
            'humidity': h
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
    run(app=app, port=8888)

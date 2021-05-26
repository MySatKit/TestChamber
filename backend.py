from fastapi import FastAPI, Request
from uvicorn import run
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from os import environ


app = FastAPI()
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
    if not dummy:
        t, p, h = read_BME280_all(my_i2c_bus)
    else:
        t = 26
        p = 1008
        h = 59
    return templates.TemplateResponse("root.html", {"request": request,
                                                    "temperature": t,
                                                    "pressure": p,
                                                    "humidity": h}
                                      )


@app.get("/update")
async def update():
    if not dummy:
        t, p, h = read_BME280_all(my_i2c_bus)
    else:
        t = 26
        p = 1008
        h = 59
    return [t, p, h]


if __name__ == '__main__':
    run(app=app, port=8888)

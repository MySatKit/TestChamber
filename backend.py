from fastapi import FastAPI
from uvicorn import run

from bme280 import read_BME280_all, DEVICE
from my_i2c import MyI2CBus

app = FastAPI()

my_i2c_bus = MyI2CBus(1)


@app.get("/")
async def root():
    t, p, h = read_BME280_all(my_i2c_bus)
    return [t, p, h]


@app.get("/update")
async def update():
    t, p, h = read_BME280_all(my_i2c_bus)
    return [t, p, h]


if __name__ == '__main__':
    run(app=app, port=8888)

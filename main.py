import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import settings

# Init settings
settings.init()

# Create app
app = FastAPI()

# Enable CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add process time to response's header
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    print(start_time)
    response = await call_next(request)
    process_time = time.time() - start_time
    print(process_time)
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Close http session when shutdown app
@app.on_event("shutdown")
async def shutdown_event():
    await settings.http_client.close()


# Import routers
from routers import auth
# , asset_tree, timeseries, alarm, asset, meter, device_profile, gateway, dashboard, env_sensor, consumption
app.include_router(auth.router)
# app.include_router(asset_tree.router)
# app.include_router(asset.router)
# app.include_router(device_profile.router)
# app.include_router(meter.router)
# app.include_router(gateway.router)
# app.include_router(timeseries.router)
# app.include_router(alarm.router)
# app.include_router(dashboard.router)
# app.include_router(env_sensor.router)
# app.include_router(consumption.router)
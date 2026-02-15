from fastapi import FastAPI
from pulsecheck_py.fastapi import make_health_router
from pulsecheck_py.core import HealthRegistry

app = FastAPI()

registry = HealthRegistry(environment="local")

app.include_router(make_health_router(registry))

@app.get("/")
def root():
    return {"ok": True}

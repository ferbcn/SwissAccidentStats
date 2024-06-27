import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.wsgi import WSGIMiddleware
from dash_unfaelle_map import app as dash_app
from dash_unfaelle_animation_years import app as dash_app_anim

# Define the FastAPI server
app = FastAPI()

# Mount the Dash app as a sub-application in the FastAPI server
app.mount("/map", WSGIMiddleware(dash_app.server))
app.mount("/anim", WSGIMiddleware(dash_app_anim.server))


@app.on_event("startup")
def startup_event():
    print("Starting Dash App...")

@app.get("/")
def index():
    return RedirectResponse(url="/map")


# Start the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
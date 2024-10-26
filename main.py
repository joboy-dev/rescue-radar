import time
from fastapi.exceptions import RequestValidationError
import uvicorn
from fastapi import (
    FastAPI,
    HTTPException, 
    Request, 
    templating, 
    staticfiles, 
    concurrency
)
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.exc import IntegrityError

from api.core.dependencies.context import add_template_context
from api.utils.settings import settings
from api.utils.logger import app_logger
from api.v1.routes import v1_router


app = FastAPI(title='Rescue Radar')

@concurrency.asynccontextmanager
async def lifespan(app: FastAPI):
    yield

# Set up session middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Middleware to log details after each request
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Capture request start time
    start_time = time.time()

    # Process the request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time
    formatted_process_time = f"{process_time:.3f}s"

    # Capture request and response details
    client_ip = request.client.host
    method = request.method
    url = request.url.path
    status_code = response.status_code

    # Format the log string similar to your example
    log_string = (
        f"{client_ip} - \"{method} {url} HTTP/1.1\" {status_code} - {formatted_process_time}"
    )

    # Log the formatted string
    app_logger.info(log_string)

    return response
    
# Set up frontend templates
frontend = templating.Jinja2Templates('frontend/templates')

# Mount static files
app.mount("/static", staticfiles.StaticFiles(directory="frontend/static"), name="static")

# Include all routes
app.include_router(v1_router)

# Set up index route
@app.get('/')
@add_template_context('pages/index.html')
async def index(request: Request):
    return {}


@app.exception_handler(HTTPException)
async def http_exception(request: Request, exc: HTTPException):
    """HTTP exception handler"""

    app_logger.info(f"HTTPException: {request.url.path} | {exc.status_code} | {exc.detail}")

    # return JSONResponse(
    #     status_code=exc.status_code,
    #     content={
    #         "status": False,
    #         "status_code": exc.status_code,
    #         "message": exc.detail,
    #     },
    # )


@app.exception_handler(RequestValidationError)
async def validation_exception(request: Request, exc: RequestValidationError):
    """Validation exception handler"""

    errors = [
        {"loc": error["loc"], "msg": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]

    app_logger.info(f"RequestValidationError: {request.url.path} | {errors}")

    # return JSONResponse(
    #     status_code=422,
    #     content={
    #         "status": False,
    #         "status_code": 422,
    #         "message": "Invalid input",
    #         "errors": errors,
    #     },
    # )


@app.exception_handler(IntegrityError)
async def integrity_exception(request: Request, exc: IntegrityError):
    """Integrity error exception handlers"""

    app_logger.info(f"Exception occured: {request.url.path} | 500 | {exc}")

    # return JSONResponse(
    #     status_code=500,
    #     content={
    #         "status": False,
    #         "status_code": 500,
    #         "message": f"An unexpected error occurred: {exc}",
    #     },
    # )


@app.exception_handler(Exception)
async def exception(request: Request, exc: Exception):
    """Other exception handlers"""

    app_logger.info(f"Exception occured | {request.url.path} | 500 | {exc}")

    # return JSONResponse(
    #     status_code=500,
    #     content={
    #         "status": False,
    #         "status_code": 500,
    #         "message": f"An unexpected error occurred: {exc}",
    #     },
    # )


# Run app
if __name__ == '__main__':
    uvicorn.run(
        'main:app', 
        host='0.0.0.0', 
        port=8001,
        reload=True,
        reload_excludes=['main.py']
    )

"""
Runs the app
"""
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException


app = FastAPI(default_response_class=HTMLResponse, openapi_url=None)

template_path = Path(__file__).resolve().parent / 'html'
templates = Jinja2Templates(directory=str(template_path))


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> HTMLResponse:
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return templates.TemplateResponse(
            name='404.html',
            context={'request': request},
            status_code=status.HTTP_404_NOT_FOUND
        )
    else:
        return await http_exception_handler(request, exc)


@app.get('/')
async def home(request: Request) -> HTMLResponse:
    """
    Shows the homepage
    """
    return templates.TemplateResponse(
        name='test.html',
        context={'request': request}
    )

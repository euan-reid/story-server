"""
Runs the app
"""
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from google.cloud import datastore
from starlette.exceptions import HTTPException as StarletteHTTPException

from content_models import categories_literal
from config import settings
from datastore_model import DatastoreModel

client = datastore.Client()
app = FastAPI(default_response_class=HTMLResponse, openapi_url=None)

template_path = Path(__file__).resolve().parent / 'html'
templates = Jinja2Templates(directory=str(template_path))


def format_template(
    request: Request,
    category: str,
    resource: DatastoreModel
) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        name=f'{category}.html',
        context={
            'settings': settings,
            'request': request,
            'resource': resource
        }
    )


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> HTMLResponse:
    """
    Renders a 404 template page for 404 errors, otherwise use default behaviour
    """
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return templates.TemplateResponse(
            name='404.html',
            context={'request': request, 'settings': settings},
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
        context={'request': request, 'settings': settings},
    )


@app.get('/{category}/{name}')
async def page(
    request: Request,
    category: categories_literal,
    name: str
) -> HTMLResponse:
    """
    Shows a page
    """
    resource = DatastoreModel.from_type_and_name(category, name)

    if resource is None:
        raise StarletteHTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return format_template(request, category, resource)

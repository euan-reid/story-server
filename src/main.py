"""
Runs the app
"""
from pathlib import Path
from typing import Union

from fastapi import FastAPI, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from google.cloud import datastore
from pydantic.types import UUID4
from starlette.exceptions import HTTPException as StarletteHTTPException

import models

client = datastore.Client()
app = FastAPI(default_response_class=HTMLResponse, openapi_url=None)

template_path = Path(__file__).resolve().parent / 'html'
templates = Jinja2Templates(directory=str(template_path))


def format_template(
    request: Request,
    header_title: str,
    page_title: str,
    category: str,
    resource: models.DatastoreModel
) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        name=f'{category}.html',
        context={
            'header_title': header_title,
            'page_title': page_title,
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


@app.get('/{category}/{item_id}')
async def page(
    request: Request,
    category: models.categories_literal,
    item_id: Union[UUID4, str]
) -> HTMLResponse:
    """
    Shows a page
    """
    resource = models.DatastoreModel.from_type_and_lookup(category, item_id)

    if resource is None:
        raise StarletteHTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return format_template(request, resource.name, resource.name, category, resource)

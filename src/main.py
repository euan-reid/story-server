"""
Runs the app
"""
from pathlib import Path
from typing import Type

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
    page_title: str,
    category: str,
    resource: Type[models.DatastoreModel]
) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        name=f'{category}.html',
        context={
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


@app.get('/authorbyname/{name}', response_model=models.Author)
async def author_by_name(request: Request, name: str) -> models.Author:
    author = models.Author.from_name(name)

    if author is None:
        raise StarletteHTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return format_template(request, author.name, 'author', author)


@app.get('/{category}/{item_id}')
async def page(
    request: Request,
    category: models.categories_literal,
    item_id: UUID4
) -> HTMLResponse:
    """
    Shows a page
    """
    resource = models.DatastoreModel.from_type_and_id(
        subclass_name=category,
        id=item_id
    )

    if resource is None:
        raise StarletteHTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return format_template(request, resource.name, category, resource)

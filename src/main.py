"""
Runs the app
"""
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from google.cloud import datastore
from pydantic.types import UUID4
from starlette.exceptions import HTTPException as StarletteHTTPException

from models import categories_literal, DatastoreModel

client = datastore.Client()
app = FastAPI(default_response_class=HTMLResponse, openapi_url=None)

template_path = Path(__file__).resolve().parent / 'html'
templates = Jinja2Templates(directory=str(template_path))


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
    category: categories_literal,
    item_id: UUID4
) -> HTMLResponse:
    """
    Shows a page
    """
    resource = DatastoreModel.from_type_and_id(
        subclass_name=category,
        id=item_id
    )

    if resource is None:
        raise StarletteHTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        name=f'{category}.html',
        context={'request': request, 'id': item_id, 'resource': resource}
    )

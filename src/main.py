"""Run the app."""
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.templating import _TemplateResponse as TemplateResponse

from config import settings
from content_models import CategoriesLiteral
from datastore_model import DatastoreModel

app = FastAPI(default_response_class=TemplateResponse, openapi_url=None)

template_path = Path(__file__).resolve().parent / 'html'
templates = Jinja2Templates(directory=str(template_path))


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> Response:
    """Render template pages for anticipatable errors. Fall back to default."""
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return templates.TemplateResponse(
            name='404.html',
            context={'request': request, 'settings': settings},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return await http_exception_handler(request, exc)


@app.get('/')
async def home(request: Request) -> TemplateResponse:
    """Show the homepage."""
    return templates.TemplateResponse(
        name='test.html',
        context={'request': request, 'settings': settings},
    )


@app.get('/{category}/{name}')
async def page(
    request: Request,
    category: CategoriesLiteral,  # type: ignore
    name: str,
) -> TemplateResponse:
    """Show a page."""
    resource = DatastoreModel.from_subclass_and_name(category, name)

    if resource is None:
        raise StarletteHTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        name=f'{category}.html',
        context={
            'settings': settings,
            'request': request,
            'resource': resource,
        },
    )

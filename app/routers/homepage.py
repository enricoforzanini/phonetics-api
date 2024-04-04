from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context
from typing import Any

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

# From https://stackoverflow.com/a/77835272
@pass_context
def urlx_for(context: dict, name: str, **path_params: Any, ) -> str:
    request: Request = context['request']
    http_url = request.url_for(name, **path_params)
    if scheme := request.headers.get('x-forwarded-proto'):
        return http_url.replace(scheme=scheme)
    return http_url

templates.env.globals['url_for'] = urlx_for

@router.get("/homepage", response_class=HTMLResponse)
async def frontend(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

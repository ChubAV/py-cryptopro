from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from .dependencies import get_templates, get_context

html_router = APIRouter()


@html_router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    context: Annotated[dict, Depends(get_context)],
):
    return templates.TemplateResponse(
        request=request, name="home.html", context={**context, "current_page": "home"}
    )


@html_router.get("/about/", response_class=HTMLResponse)
async def about(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    context: Annotated[dict, Depends(get_context)],
):
    return templates.TemplateResponse(
        request=request, name="about.html", context={**context, "current_page": "about"}
    )


@html_router.get("/cadesplugin/", response_class=HTMLResponse)
async def cadesplugin(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    context: Annotated[dict, Depends(get_context)],
):
    return templates.TemplateResponse(
        request=request,
        name="cadesplugin.html",
        context={**context, "current_page": "cadesplugin"},
    )


@html_router.get("/hash/", response_class=HTMLResponse)
async def hash(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    context: Annotated[dict, Depends(get_context)],
):
    return templates.TemplateResponse(
        request=request, name="hash.html", context={**context, "current_page": "hash"}
    )


@html_router.get("/verifytxt/", response_class=HTMLResponse)
async def verifytxt(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    context: Annotated[dict, Depends(get_context)],
):
    return templates.TemplateResponse(
        request=request,
        name="verifytxt.html",
        context={**context, "current_page": "verifytxt"},
    )


@html_router.get("/verifyfile/", response_class=HTMLResponse)
async def verifyfile(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    context: Annotated[dict, Depends(get_context)],
):
    return templates.TemplateResponse(
        request=request,
        name="verifyfile.html",
        context={**context, "current_page": "verifyfile"},
    )


@html_router.get("/verifyxml/", response_class=HTMLResponse)
async def verifyxml(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    context: Annotated[dict, Depends(get_context)],
):
    return templates.TemplateResponse(
        request=request,
        name="verifyxml.html",
        context={**context, "current_page": "verifyxml"},
    )


@html_router.get("/certificates/", response_class=HTMLResponse)
async def certificates(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    context: Annotated[dict, Depends(get_context)],
):
    return templates.TemplateResponse(
        request=request,
        name="certificates.html",
        context={**context, "current_page": "certificates"},
    )


@html_router.get("/certificate/", response_class=HTMLResponse)
async def certificate(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    context: Annotated[dict, Depends(get_context)],
):
    return templates.TemplateResponse(
        request=request,
        name="certificate.html",
        context={**context, "current_page": "certificate"},
    )


@html_router.get("/certs_import/", response_class=HTMLResponse)
async def certs_import(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    context: Annotated[dict, Depends(get_context)],
):
    return templates.TemplateResponse(
        request=request,
        name="certs_import.html",
        context={**context, "current_page": "certs_import"},
    )


@html_router.get("/signtxt/", response_class=HTMLResponse)
async def signtxt(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    context: Annotated[dict, Depends(get_context)],
):
    return templates.TemplateResponse(
        request=request,
        name="signtxt.html",
        context={**context, "current_page": "signtxt"},
    )


@html_router.get("/signfile/", response_class=HTMLResponse)
async def signfile(
    request: Request,
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    context: Annotated[dict, Depends(get_context)],
):
    return templates.TemplateResponse(
        request=request,
        name="signfile.html",
        context={**context, "current_page": "signfile"},
    )

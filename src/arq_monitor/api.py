"""
Api routes
"""

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.schemas import SchemaGenerator

from .config import logger, TEMPLATES
from .utils import create_new_job, get_jobs_data

schemas = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "arq-monitor", "version": "0.1"}}
)

async def get_jobs(request: Request):
    """
    responses:
        200:
            description: List of jobs.
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            status:
                                type: string
                                description: status
                            updated_at:
                                type: string
                                description: ISO formatted time
                            results:
                                type: object
                                description: processed jobs
                            queues:
                                type: object
                                description: jobs in given queue
        500:
            description: Server error.
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            status:
                                type: string
                                description: status
                            detail:
                                type: string
                                description: info on error
    """
    try:
        data = await get_jobs_data(arq_conn=request.state.arq_conn)
        response = JSONResponse(
            content={"status": "success", **data},
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response

async def create_job(request: Request):
    """
    requestBody:
        required: true
        content:
            application/json:
                schema:
                    type: object
                    required:
                        - function
                        - _queue_name
                    properties:
                        function:
                            type: string
                            description: function name
                        args:
                            type: array
                            description: args to be passed to function
                        kwargs:
                            type: object
                            description: kwargs to be passed to function
                        _queue_name:
                            type: string
                            description: queue name
    responses:
        201:
            description: Job created.
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            status:
                                type: string
                                description: status
                            job_id:
                                type: string
                                description: job_id of created job
        400:
            description: Job not created.
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            status:
                                type: string
                                description: status
                            detail:
                                type: string
                                description: info on error
        500:
            description: Server error.
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            status:
                                type: string
                                description: status
                            detail:
                                type: string
                                description: info on error
    """
    try:
        data = await request.json()
        job = await create_new_job(arq_conn=request.state.arq_conn, kwargs=data)
        if job is None:
            response = JSONResponse(
                content={"status": "error", "detail": "job not created"},
                status_code=400
            )
        else:
            response = JSONResponse(
                content={"status": "success", "job_id": job.job_id},
                status_code=201
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response

def openapi_schema(request: Request):
    """
    Api schema
    """
    return schemas.OpenAPIResponse(request=request)

def docs(request: Request):
    """
    Automatic docs based on api schema
    """
    response = TEMPLATES.TemplateResponse(
        request=request,
        name="docs.html.jinja",
        context={}
    )
    return response

api_routes = [
    # api
    Route(path='/jobs', endpoint=get_jobs, methods=["GET", ], name="get_jobs"),
    Route(path='/jobs', endpoint=create_job, methods=["POST", ], name="create_job"),
    # docs
    Route(path="/docs", endpoint=docs, include_in_schema=False),
    Route(path="/schema", endpoint=openapi_schema, include_in_schema=False),
]
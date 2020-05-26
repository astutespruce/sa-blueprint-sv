"""
TODO:
* validate max size (on nginx side)
"""

import logging
from pathlib import Path
import os
import shutil
import tempfile
from typing import Optional
from zipfile import ZipFile

import arq

from arq.jobs import Job, JobStatus
from fastapi import (
    FastAPI,
    File,
    UploadFile,
    Form,
    HTTPException,
    Depends,
    Security,
    BackgroundTasks,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from fastapi.requests import Request
from fastapi.responses import Response, FileResponse
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from api.errors import DataError
from api.geo import get_dataset
from api.custom_report import create_custom_report
from api.settings import (
    LOGGING_LEVEL,
    REDIS,
    API_TOKEN,
    TEMP_DIR,
    ALLOWED_ORIGINS,
    SENTRY_DSN,
)
from api.progress import get_progress


log = logging.getLogger(__name__)
log.setLevel(LOGGING_LEVEL)

### Create the main API app
app = FastAPI()

if SENTRY_DSN:
    log.info("setting up sentry")
    sentry_sdk.init(dsn=SENTRY_DSN)
    app.add_middleware(SentryAsgiMiddleware)


async def catch_exceptions_middleware(request: Request, call_next):
    """Middleware that wraps HTTP requests and catches exceptions.

    These need to be caught here in order to ensure that the
    CORS middleware is used for the response, otherwise the client
    gets CORS related errors instead of the actual error.

    Parameters
    ----------
    request : Request
    call_next : func
        next func in the chain to call
    """
    try:
        return await call_next(request)

    except Exception as ex:
        log.error(f"Error processing request: {ex}")
        return Response("Internal server error", status_code=500)


app.middleware("http")(catch_exceptions_middleware)


### Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


def get_token(token: str = Security(APIKeyQuery(name="token", auto_error=False))):
    """Get token from query parameters and test against known TOKEN.

    Parameters
    ----------
    token : str

    Returns
    -------
    str
        returns token if it matches known TOKEN, otherwise raises HTTPException.
    """
    if token == API_TOKEN:
        return token

    raise HTTPException(status_code=403, detail="Invalid token")


def save_file(file: UploadFile) -> Path:
    """Save file to a temporary directory and return the path.

    The caller is responsible for deleting the file.

    Parameters
    ----------
    file : UploadFile
        file received from API endpoint.

    Returns
    -------
    Path
    """

    try:
        suffix = Path(file.filename).suffix

        fp, name = tempfile.mkstemp(suffix=suffix, dir=TEMP_DIR)
        with open(fp, "wb") as out:
            shutil.copyfileobj(file.file, out)

    finally:
        # always close the file handle from the API handler
        file.file.close()

    return Path(name)


@app.post("/api/reports/custom")
async def custom_report_endpoint(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    token: APIKey = Depends(get_token),
):
    if file.content_type != "application/zip":
        log.error(f"Invalid upload content type: {file.content_type}")

        raise HTTPException(
            status_code=400,
            detail="file must be a zip file containing shapefile or file geodatabase",
        )

    filename = save_file(file)
    log.debug(f"upload saved to: {filename}")

    ### validate that upload has a shapefile or FGDB
    try:
        dataset, layer = get_dataset(ZipFile(filename))

    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))

    ### Create report task
    try:
        redis = await arq.create_pool(REDIS)
        job = await redis.enqueue_job(
            "create_custom_report", filename, dataset, layer, name=name
        )

    except Exception as ex:
        log.error(f"Error creating background task, is Redis offline?  {ex}")
        raise HTTPException(status_code=500, detail="Internal server error")

    return {"job": job.job_id}


@app.get("/api/reports/status/{job_id}")
async def job_status_endpoint(job_id: str):
    """Return the status of a job.

    Job status values derived from JobStatus enum at:
    https://github.com/samuelcolvin/arq/blob/master/arq/jobs.py
    ['deferred', 'queued', 'in_progress', 'complete', 'not_found']

    We add ['success', 'failed'] status values here.

    Parameters
    ----------
    job_id : str

    Returns
    -------
    JSON
        {"status": "...", "progress": 0-100, "result": "...only if complete...", "detail": "...only if failed..."}
    """
    redis = await arq.create_pool(REDIS)
    job = Job(job_id, redis=redis)
    status = await job.status()

    if status == JobStatus.not_found:
        raise HTTPException(status_code=404, detail="Job not found")

    if status != JobStatus.complete:
        progress = await get_progress(job_id)
        return {"status": status, "progress": progress}

    info = await job.result_info()

    if info.success:
        return {"status": "success", "result": f"/api/reports/results/{job_id}"}

    status = "failed"

    try:
        # this re-raises the underlying exception raised in the worker
        await job.result()

    except DataError as ex:
        message = str(ex)

    # TODO: other specific exceptions

    except Exception as ex:
        log.error(ex)
        message = "Internal server error"
        raise HTTPException(status_code=500, detail="Internal server error")

    return {"status": status, "detail": message}


@app.get("/api/reports/results/{job_id}")
async def report_pdf_endpoint(job_id: str):
    redis = await arq.create_pool(REDIS)
    job = Job(job_id, redis=redis)
    status = await job.status()

    if status == JobStatus.not_found:
        raise HTTPException(status_code=404, detail="Job not found")

    if status != JobStatus.complete:
        raise HTTPException(status_code=400, detail="Job not complete")

    info = await job.result_info()
    if not info.success:
        raise HTTPException(status_code=400, detail="Job failed, cannot return results")

    path = info.result
    name = info.kwargs.get("name", None) or "Blueprint Summary Report"

    return FileResponse(path, filename=f"{name}.pdf", media_type="application/pdf")

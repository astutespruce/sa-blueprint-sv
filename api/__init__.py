"""
TODO:
* validate max size (on nginx side)
* add CORS support (either here or nginx)
* background task:
"""

import logging
from pathlib import Path
import os
import shutil
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

from dotenv import load_dotenv
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
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
from fastapi.responses import Response

from api.geo import get_dataset
from api.custom_report import create_custom_report


load_dotenv()
TOKEN = os.getenv("API_TOKEN")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")

log = logging.getLogger(__name__)
log.setLevel(LOGGING_LEVEL)

app = FastAPI()


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
    if token == TOKEN:
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

        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)

    finally:
        file.file.close()

    return tmp_path


def delete_file(path: str):
    print(f"Deleting {path}...")
    if path.exists():
        path.unlink()


@app.post("/report/custom/")
async def custom_report_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    token: APIKey = Depends(get_token),
):
    if file.content_type != "application/zip":
        # TODO: enable support for application/x-7z-compressed?

        log.error(f"Invalid upload content type: {file.content_type}")

        raise HTTPException(
            status_code=400,
            detail="file must be a zip file containing shapefile or file geodatabase",
        )

    filename = save_file(file)
    log.debug(f"upload saved to: {filename}")
    background_tasks.add_task(delete_file, filename)

    ### validate that upload has a shapefile or FGDB
    try:
        dataset, layer = get_dataset(ZipFile(filename))

    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))

    ### create the report
    try:
        pdf = create_custom_report(filename, dataset, layer, name)

    except ValueError:
        raise HTTPException(status_code=400, detail=str(ex))

    return Response(
        content=pdf,
        status_code=200,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment;{name}.pdf"},
    )

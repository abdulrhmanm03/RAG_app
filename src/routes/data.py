import logging

import aiofiles
from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic.json_schema import JsonRef

from src.controllers import DataController, ProjectController
from src.utils.config import Settings, get_settings

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter()


@data_router.post("/upload/{project_id}")
async def upload_data(
    project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)
):
    data_controller = DataController()

    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"signal": result_signal}
        )
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_filepath(
        orig_file_name=file.filename, project_id=project_id  # type: ignore
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chuck := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chuck)
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": "File upload failed"},
        )
    return JSONResponse(content={"signal": "File uploaded", "file_id": file_id})

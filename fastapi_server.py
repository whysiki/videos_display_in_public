from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from generate_mpeg import get_video_dash_output
from emcrypt_str import decrypt_str, encrypt_str
from pathlib import Path
from typing import Dict
from starlette.requests import Request
import os
from rich import print

app = FastAPI()
current_path = Path(__file__).parent
templates = Jinja2Templates(directory=current_path / "templates")
static_path = current_path / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

video_dashpath_encryptstr_dict: Dict[str, str] = {
    str(video): encrypt_str(str(get_video_dash_output(video)))
    for video in (current_path / "static" / "videos").glob("*.mp4")
}

print(video_dashpath_encryptstr_dict)


@app.get("/dash/{dashpath_encryptstr}/{filename:path}")
async def dash(dashpath_encryptstr: str, filename: str):
    dashpath = decrypt_str(dashpath_encryptstr)
    dashpathPath = Path(dashpath)
    if not dashpathPath.exists():
        raise HTTPException(status_code=404, detail="Path not found")
    file_path = dashpathPath / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(current_path / "static" / "favicon.ico")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "video_dashpath_encryptstr_dict": video_dashpath_encryptstr_dict,
            "enumerate": enumerate,
        },
    )


if __name__ == "__main__":
    current_file = Path(__file__)

    port = 51231
    command = (
        f"start cmd /k python -m uvicorn {current_file.stem}:app --port {port} --reload"
    )
    print(command)
    os.system(command)

# coding: utf-8
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from generate_mpeg import (
    get_video_dash_output,
    rediect_file_to_base64str_decarator,
    get_thumbnail_path,
    thumbnail_path_pattern,
    dash_output_path_pattern,
)
from emcrypt_str import decrypt_str, encrypt_str
from pathlib import Path
from typing import Dict, List
from starlette.requests import Request
import os
from rich import print
from dataclasses import dataclass
import asyncio
import shutil
from contextlib import asynccontextmanager
from loguru import logger

current_path = Path(__file__).parent
static_path = current_path / "static"
videos_path = current_path / "videos"
templates_path = current_path / "templates"
templates = Jinja2Templates(directory=templates_path)
port = 51231


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_videos(app)  # 启动时执行 initialize_videos 函数
    logger.success(f"Videos initialized, serving on http://localhost:{port}")
    yield  # yield 之前的代码在启动时执行，yield 之后的代码在关闭时执行


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory=static_path), name="static")


@dataclass
class VideoInfo:
    video_path: Path
    dashpath_encryptstr: str = ""
    video_thumbnail_base64str: str = ""

    def __post_init__(self):
        self.loop = asyncio.get_event_loop()
        self.async_generation_tasks = [
            self.loop.create_task(self.__generate_thumbnail_base64str()),
            self.loop.create_task(self.__generate_encrypted_dashpath()),
        ]

    async def gather_async_operations(self):
        await asyncio.gather(*self.async_generation_tasks)

    async def __generate_encrypted_dashpath(self):
        self.dashpath_encryptstr = encrypt_str(
            str(get_video_dash_output(self.video_path))
        )

    async def __generate_thumbnail_base64str(self):
        self.video_thumbnail_base64str = rediect_file_to_base64str_decarator(
            get_thumbnail_path
        )(self.video_path)

    @property
    def dashpath(self) -> Path:
        return dash_output_path_pattern(self.video_path)

    @property
    def thumbnail_path(self) -> Path:
        return thumbnail_path_pattern(self.video_path)

    def clear_cache(self):
        try:
            shutil.rmtree(self.dashpath.parent)
        except FileNotFoundError:
            pass
        try:
            shutil.rmtree(self.thumbnail_path.parent)
        except FileNotFoundError:
            pass


# {parent_dir: {video_path: VideoInfo}}
async def initialize_videos(app: FastAPI):
    videos_display_dict: Dict[str, Dict[str, VideoInfo]] = {}
    all_async_generation_tasks = []
    for video in videos_path.glob("**/*.mp4"):
        parent_dir = str(video.parent.relative_to(videos_path))
        parent_dir = parent_dir if parent_dir != "." else "root"
        if parent_dir not in videos_display_dict:
            videos_display_dict[parent_dir] = {}
        video_info = VideoInfo(video)
        all_async_generation_tasks.append(video_info.gather_async_operations())
        videos_display_dict[parent_dir][str(video)] = video_info
    await asyncio.gather(*all_async_generation_tasks)
    app.state.videos_display_dict = videos_display_dict


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


@app.get("/video/{dashpath_encryptstr}", response_class=HTMLResponse)
async def video_detail(request: Request, dashpath_encryptstr: str):
    video_path = decrypt_str(dashpath_encryptstr)
    print(video_path)
    return templates.TemplateResponse(
        "video_detail.html",
        {
            "request": request,
            "video_path": video_path,
            "dashpath_encryptstr": dashpath_encryptstr,
            "Path": Path,
        },
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    videos_display_dict = request.app.state.videos_display_dict
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "videos_display_dict": videos_display_dict,
            "enumerate": enumerate,
            "Path": Path,
            "videos_path": videos_path,
        },
    )


if __name__ == "__main__":
    current_file = Path(__file__)

    # start cmd /k
    command = f"python -m uvicorn {current_file.stem}:app --port {port} --reload --reload-dir {static_path.as_posix()}"
    print(command)
    os.system(command)

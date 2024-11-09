from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from generate_mpeg import get_video_dash_output
from pathlib import Path
from emcrypt_str import decrypt_str, encrypt_str
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()

css_path = Path(__file__).parent / "static" / "css"

app.mount("/static", StaticFiles(directory=(Path(__file__).parent / "static")))

current_path = Path(__file__).parent

video_dashpath_encryptstr_dict: dict[str, str] = {
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


def generate_videos_html(video_dashpath_encryptstr_dict: dict[str, Path]) -> str:
    video_html = ""
    for index, (video, dashpath_encryptstr) in enumerate(
        video_dashpath_encryptstr_dict.items()
    ):
        video_html += f"""
        <div id='video{index}' class='video'>
            <h2>{Path(video).stem}</h2>
            <video id="videoPlayer{index}" width="640" height="360" controls>
                <source src="/dash/{dashpath_encryptstr}/manifest.mpd" type="application/dash+xml">
            </video>
            <script src="https://cdn.dashjs.org/latest/dash.all.min.js"></script>
            <script>
                var url_{index} = "/dash/{dashpath_encryptstr}/manifest.mpd";
                var player_{index} = dashjs.MediaPlayer().create();
                player_{index}.initialize(document.querySelector("#videoPlayer{index}"), url_{index}, true);
            </script>
        </div>
        """
    return video_html


@app.get("/", response_class=HTMLResponse)
async def index():
    home_html: str = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>MPEG-DASH Demo</title>
        {
            "".join
            ([
                f'<link rel="stylesheet" href="{(css_file.relative_to(current_path)).as_posix()}">'
                for css_file in css_path.glob("*.css")
            ])
        }
    </head>
    <body>
        <h1> Video List </h1>
        {generate_videos_html(video_dashpath_encryptstr_dict)}
    </body>
    </html>
    """
    return home_html


if __name__ == "__main__":
    current_file = Path(__file__)

    command = f"python -m uvicorn {current_file.stem}:app --port 51231"
    print(command)
    os.system(command)

from flask import Flask, send_from_directory
from generate_mpeg import get_video_dash_output
from pathlib import Path
from emcrypt_str import decrypt_str, encrypt_str

app = Flask(__name__)

current_path = Path(__file__).parent

video_dashpath_encryptstr_dict: dict[str, str] = {
    str(video): encrypt_str(str(get_video_dash_output(video)))
    for video in (current_path / "static" / "videos").glob("*.mp4")
}

print(video_dashpath_encryptstr_dict)


@app.route("/dash/<dashpath_encryptstr>/<path:filename>")
def dash(dashpath_encryptstr, filename):
    dashpath = decrypt_str(dashpath_encryptstr)
    dashpathPath = Path(dashpath)
    if not dashpathPath.exists():
        return "Path not found", 404
    return send_from_directory(dashpathPath, filename)


def generate_videos_html(video_dashpath_encryptstr_dict: dict[str, Path]) -> str:
    video_html = ""
    for index, (video, dashpath_encryptstr) in enumerate(
        video_dashpath_encryptstr_dict.items()
    ):
        video_html += f"""
        <div id='video{index}' style="margin-bottom: 20px;">
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


@app.route("/")
def index():
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>MPEG-DASH Demo</title>
    </head>
    <body>
        <h1> MPEG-DASH Video Stream </h1>
        {generate_videos_html(video_dashpath_encryptstr_dict)}
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

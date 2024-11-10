import subprocess
from pathlib import Path
from rich import print
import base64


def dash_output_path_pattern(video_path: Path) -> Path:
    """
    生成输出文件夹路径
    """
    return video_path.parent / "video_dash_output" / f"{video_path.stem}"


def manifest_path_pattern(output_path: Path) -> Path:
    """
    生成manifest.mpd文件路径
    """
    return output_path / "manifest.mpd"


def thumbnail_path_pattern(video_path: Path) -> Path:
    """
    生成缩略图文件路径
    """
    return video_path.parent / "thumbnails" / f"{video_path.stem}.jpg"


def generate_mpeg(video_path: Path) -> bool:
    assert video_path.exists(), "video not found"
    # 输出文件夹路径
    dash_output_folder = dash_output_path_pattern(video_path)
    dash_output_folder.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-loglevel",
        "error",
        "-i",
        str(video_path.absolute()),  # 输入文件
        # video_path.name,
        "-map",
        "0:v",  # 选择视频流
        "-map",
        "0:a",  # 选择音频流
        "-b:v",
        "1500k",  # 视频流的比特率
        "-b:a",
        "128k",  # 音频流的比特率
        "-c:v",
        # "libx264",  # 视频编码器
        "copy",
        "-preset",
        # "fast",  # 编码速度
        "ultrafast",
        "-c:a",
        "aac",  # 音频编码器
        "-f",
        "dash",  # 输出格式
        "-seg_duration",
        "2",  # 片段长度
        "-adaptation_sets",
        "id=0,streams=v id=1,streams=a",  # 视频和音频流设置
        # str(manifest_path_pattern(output_path).absolute()),  # 输出清单文件
        manifest_path_pattern(dash_output_folder).name,
    ]
    try:
        result = subprocess.run(
            command,
            cwd=dash_output_folder,  # 设置工作目录
            # capture_output=True,
            # text=True,
            check=True,
        )
        # print(result.stdout)
        # print(result.stderr)
        print("MPEG-DASH video generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def get_video_dash_output(video_path: Path) -> Path:
    dash_output_directory = dash_output_path_pattern(video_path)
    m4s_files = list(dash_output_directory.glob("*.m4s"))
    if len(m4s_files) == 0 or not manifest_path_pattern(dash_output_directory).exists():
        print("MPEG-DASH video not found,will generate it")
        if not generate_mpeg(video_path):
            raise FileNotFoundError("MPEG-DASH video dash not found")
    assert dash_output_directory.exists(), "output folder not found" + str(
        dash_output_directory
    )
    assert manifest_path_pattern(
        dash_output_directory
    ).exists(), "manifest.mpd not found"
    return dash_output_directory


def generate_thumbnail(video_path: Path) -> bool:
    assert video_path.exists(), "video not found"
    assert video_path.suffix in [".mp4", ".mkv", ".avi"], "video format not supported"
    output_thumb_file_path: Path = thumbnail_path_pattern(video_path)
    output_thumb_file_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-loglevel",
        "error",
        "-i",
        str(video_path.absolute()),  # 输入文件
        "-vf",
        "thumbnail",  # 使用thumbnail滤镜
        "-frames:v",
        "1",  # 只提取一帧
        "-q:v",
        "10",  # 降低图片质量以加快速度
        output_thumb_file_path.name,
    ]
    try:
        result = subprocess.run(
            command,
            # capture_output=True,
            # text=True,
            check=True,
            cwd=output_thumb_file_path.parent,
        )
        # print(result.stdout)
        # print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        return False
    except Exception as e:
        print(e)
        return False


def rediect_file_to_base64str_decarator(func):
    def wrapper(*args, **kwargs):
        file_path: Path = func(*args, **kwargs)
        file_content = file_path.read_bytes()
        base64_str = base64.b64encode(file_content).decode("utf-8")
        return base64_str

    return wrapper


# @rediect_file_to_base64str_decarator
def get_thumbnail_path(video_path: Path) -> Path:
    thunbnail_path = thumbnail_path_pattern(video_path)
    if not thunbnail_path.exists():
        print("Thumbnail not found,will generate it")
        if not generate_thumbnail(video_path):
            raise FileNotFoundError("Thumbnail not found")

    assert thunbnail_path.exists(), "Thumbnail not found"
    return thunbnail_path

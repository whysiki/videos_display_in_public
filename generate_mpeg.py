import subprocess
from pathlib import Path
from rich import print


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


def generate_mpeg(video_path: Path) -> bool:
    assert video_path.exists(), "video not found"
    # 输出文件夹路径
    output_path = dash_output_path_pattern(video_path)
    output_path.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-i",
        str(video_path.absolute()),  # 输入文件
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
        "fast",  # 编码速度
        "-c:a",
        "aac",  # 音频编码器
        "-f",
        "dash",  # 输出格式
        "-seg_duration",
        "2",  # 片段长度
        "-adaptation_sets",
        "id=0,streams=v id=1,streams=a",  # 视频和音频流设置
        str(manifest_path_pattern(output_path).absolute()),  # 输出清单文件
    ]
    try:
        result = subprocess.run(
            command,
            cwd=output_path,  # 设置工作目录
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
        print(result.stderr)
        print("MPEG-DASH video generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def get_video_dash_output(video_path: Path) -> Path:
    output_path = dash_output_path_pattern(video_path)
    m4s_files = list(output_path.glob("*.m4s"))
    if len(m4s_files) == 0 or not manifest_path_pattern(output_path).exists():
        print("MPEG-DASH video not found,will generate it")
        if not generate_mpeg(video_path):
            raise FileNotFoundError("MPEG-DASH video dash not found")
    assert output_path.exists(), "output folder not found" + str(output_path)
    assert manifest_path_pattern(output_path).exists(), "manifest.mpd not found"
    return output_path

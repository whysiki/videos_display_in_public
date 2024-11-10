import asyncio
import pytest
from pathlib import Path
import shutil
from fastapi_server import VideoInfo, videos_path
from generate_mpeg import (
    get_video_dash_output,
    rediect_file_to_base64str_decarator,
    get_thumbnail_path,
)
from emcrypt_str import decrypt_str, encrypt_str
from typing import List


@pytest.mark.asyncio
async def test_fastapi_server():
    video_infos: List[VideoInfo] = []
    test_num = 3
    for video_path in videos_path.glob("**/*.mp4"):
        print(video_path)
        video_info = VideoInfo(video_path)
        video_infos.append(video_info)
        test_num -= 1
        if test_num <= 0:
            break

    await asyncio.gather(
        *(video_info.gather_async_operations() for video_info in video_infos)
    )

    for video_info in video_infos:
        video_path_ = video_info.video_path
        dashpath_encryptstr_ = video_info.dashpath_encryptstr
        video_thumbnail_base64str_ = video_info.video_thumbnail_base64str
        dashpath_ = video_info.dashpath
        thumbnail_path_ = video_info.thumbnail_path
        print(video_path_)
        print(dashpath_encryptstr_)
        print(video_thumbnail_base64str_[:10])
        print(dashpath_)
        print(thumbnail_path_)
        assert video_path_.exists()
        assert len(dashpath_encryptstr_) > 0
        assert len(video_thumbnail_base64str_) > 0
        assert dashpath_.exists()
        assert thumbnail_path_.exists()
        print()

    for video_info in video_infos:
        video_info.clear_cache()
        assert not video_info.dashpath.exists()
        assert not video_info.thumbnail_path.exists()


def test_video_processing():
    test_video_path = Path(r"cache\test_video.mp4")
    dash_output_path = get_video_dash_output(test_video_path)
    print(dash_output_path)
    thumbnail_path = get_thumbnail_path(test_video_path)
    print(thumbnail_path)
    thumbnail_base64str = rediect_file_to_base64str_decarator(get_thumbnail_path)(
        test_video_path
    )
    print(thumbnail_base64str)

    # Ensure the generated files exist
    assert dash_output_path.exists()
    assert thumbnail_path.exists()
    assert len(thumbnail_base64str) > 0

    # Clean up
    shutil.rmtree(dash_output_path.parent)
    shutil.rmtree(thumbnail_path.parent)


def test_encrypt_decrypt():
    plain_text = "This is a secret message that we want to encrypt and keep short."
    print(f"Plain text: {plain_text}")
    # 加密
    encrypted_message = encrypt_str(plain_text)
    print(f"Encrypted (Base64): {encrypted_message}")

    # 解密
    decrypted_text = decrypt_str(encrypted_message)
    assert decrypted_text == plain_text
    print(f"Decrypted: {decrypted_text}")


if __name__ == "__main__":
    pytest.main()

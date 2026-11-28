"""Prepare browser-playable clips and composite the rendered text layer."""
import subprocess


def ffmpeg(*args):
    from imageio_ffmpeg import get_ffmpeg_exe

    result = subprocess.run(
        [get_ffmpeg_exe(), '-nostdin', '-hide_banner', '-loglevel', 'error',
         '-filter_complex_threads', '1', '-y', *map(str, args)],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode:
        raise ValueError('영상 처리 실패: ' + result.stderr.strip()[-800:])


def prepare(source, output):
    ffmpeg('-i', source, '-map', '0:v:0', '-map', '0:a:0?', '-t', '30',
           '-vf', 'scale=1080:1350:force_original_aspect_ratio=increase,crop=1080:1350,setsar=1',
           '-r', '30', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'fast',
           '-c:a', 'aac', '-movflags', '+faststart', output)


def composite(source, layer, output):
    ffmpeg('-i', source, '-i', layer, '-filter_complex',
           '[0:v]scale=1080:1350:force_original_aspect_ratio=increase,crop=1080:1350,setsar=1[clip];[clip][1:v]overlay=format=auto[v]',
           '-map', '[v]', '-map', '0:a:0?', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
           '-preset', 'fast', '-c:a', 'aac', '-movflags', '+faststart', output)

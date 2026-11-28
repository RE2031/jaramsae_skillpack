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
           '-vf', "scale='min(1080,iw)':'min(1350,ih)':force_original_aspect_ratio=decrease:force_divisible_by=2,setsar=1",
           '-r', '30', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'fast',
           '-c:a', 'aac', '-movflags', '+faststart', output)


def composite(source, layer, output, frame):
    width, height, left, top = frame
    framing = (f'[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,'
               f'crop={width}:{height},setsar=1,pad=1080:1350:{left}:{top}:color=0x161b24[clip];'
               '[clip][1:v]overlay=format=auto[v]')
    ffmpeg('-i', source, '-i', layer, '-filter_complex',
           framing,
           '-map', '[v]', '-map', '0:a:0?', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
           '-preset', 'fast', '-c:a', 'aac', '-movflags', '+faststart', output)

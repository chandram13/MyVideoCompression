# Marvish Chandra
# Updated Dec 2022

from email.mime import audio
import os
from tempfile import TemporaryFile 
import ffmpeg
 
 # specifcally for mp4 files
def videocompression(video_full_path, size_upper_bound, two_pass=True, filename_suffix ='cps_'):
    filename, extension = os.path.splittext(video_full_path)
    extension = '.mp4'
    myoutput_filename = filename + filename_suffix + extension

    # minimum requirements in bps
    total_bitrate_lower_bound = 11000
    min_audio_bitrate = 30000
    max_audio_bitrate = 260000
    min_video_bitrate = 100000

    try:
        probe = ffmpeg.probe(video_full_path)
        duration = float(probe['format']['duration'])
        audio_bitrate = float((next(s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])
    target_total_bitrate = (size_upper_bound * 1024 * 8)/ (1.073741824) * duration
    if target_total_bitrate < total_bitrate_lower_bound:
        print("This bitrate is at an extremely low rate. Stop compression.")
        return False 
    
    my_min_size = (min_audio_bitrate + min_video_bitrate) * (1.073741824 * duration) / (8 * 1024)
    if size_upper_bound < my_min_size:
        print("The quality of the video is very poor. Reccomended minimum size:', '{:,}'.format(int(my_min_size)), 'KB.")
    
    # ensure targeted audio bitrate
    if 10 * audio_bitrate > target_total_bitrate:
        audio_bitrate = target_total_bitrate / 10
        if audio_bitrate < min_audio_bitrate < target_total_bitrate:
            audio_bitrate = min_audio_bitrate
        elif audio_bitrate > max_audio_bitrate:
            audio_bitrate = max_audio_bitrate

    # ensure targeted video bitrate

    video_bitrate = target_total_bitrate - audio_bitrate
    if video_bitrate < 1000:
        print("Bitrate of {} is incredibly slow. Stop compression.".format(video_bitrate))
        return False
    
    i = ffmpeg.input(video_full_path)
    if two_pass:
        ffmpeg.output(i, os.devnull,
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                          ).overwrite_output().run()
            ffmpeg.output(i, output_file_name,
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                          ).overwrite_output().run()
    else:
        ffmpeg.output(i, output_file_name,
                        **{'c:v': 'libx264', 'b:v': video_bitrate, 'c:a': 'aac', 'b:a': audio_bitrate}
                        ).overwrite_output().run()
    if os.path.getsize(output_file_name) <= size_upper_bound * 1024:
        return output_file_name
    elif os.path.getsize(output_file_name) < os.path.getsize(video_full_path):
        return compress_video(output_filename, size_upper_bound)
    else:
        return False
    except FileNotFoundError as error:
        print("You must have the package ffmpeg installed.",error)
        return False
if __name__ == "__main__":
    file_name = compress_video('people-walking-in-nyc.mp4', 50 * 1000)
    print(file_name)

import ffmpeg
import os

def extract_images_from_video(video_file, output_dir, fps=1):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    video_name = os.path.basename(video_file)
    try:
        (
            ffmpeg
            .input(video_file)  # Set frame rate for extraction
            .output(os.path.join(output_dir, f'{video_name}_%04d.jpg'), vf='fps=' + str(fps), loglevel='quiet')
            .run(overwrite_output=True)
        )
        return output_dir
    except ffmpeg.Error as e:
        print(f"An error occurred: {e}")
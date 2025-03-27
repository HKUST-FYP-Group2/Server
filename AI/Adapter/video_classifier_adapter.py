import ffmpeg
import os

def extract_images_from_ts(ts_file, output_dir, fps=1):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        (
            ffmpeg
            .input(ts_file)  # Set frame rate for extraction
            .output(os.path.join(output_dir, 'frame_%04d.png'), vf='fps=' + str(fps))
            .run(overwrite_output=True)
        )
        print(f"Images extracted to {output_dir}")
    except ffmpeg.Error as e:
        print(f"An error occurred: {e}")
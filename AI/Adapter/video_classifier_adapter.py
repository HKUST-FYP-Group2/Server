import ffmpeg
import os

def extract_images_from_mp4(mp4_file, output_dir, fps=1):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        (
            ffmpeg
            .input(mp4_file)
            .output(os.path.join(output_dir, '%d.png'), vf='fps=' + str(fps))
            .run(overwrite_output=True)
        )
        print(f"Images extracted to {output_dir}")
    except ffmpeg.Error as e:
        print(f"An error occurred while processing {mp4_file}: {e}")

def process_videos(input_dir, output_base_dir, fps=1):
    # Iterate through all .mp4 files in the input directory
    for video_file in os.listdir(input_dir):
        if video_file.endswith('.mp4'):
            video_path = os.path.join(input_dir, video_file) # /home/user/recordings/video.mp4
            video_name = os.path.splitext(video_file)[0]  # video
            output_dir = os.path.join(output_base_dir, video_name) # /home/user/extracted_frames/video

            # Check if the video has already been processed
            if os.path.exists(output_dir) and os.listdir(output_dir):
                print(f"Skipping {video_file}, already processed.")
                continue

            print(f"Processing {video_file}...")
            extract_images_from_mp4(video_path, output_dir, fps)

if __name__ == "__main__":
    input_directory = "/home/user/recordings"
    output_directory = "/home/user/extracted_images"
    frame_rate = 1
    
    process_videos(input_directory, output_directory, frame_rate)
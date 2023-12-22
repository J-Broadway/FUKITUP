import argparse
import os
import subprocess

def extract_frame(video_path, frame_number, output_path=None):
    # Determine the filename without extension and the directory
    base_name = os.path.basename(video_path)
    file_name_without_ext = os.path.splitext(base_name)[0]
    directory = os.path.dirname(video_path)

    # Set the default output path if not provided
    if not output_path:
        output_path = os.path.join(directory, f"{file_name_without_ext}_{frame_number}.jpg")

    # This checks if the output path is provided as an argument and updates accordingly
    if output_path:
        # If only a directory is provided, concatenate the default filename
        if os.path.isdir(output_path):
            output_path = os.path.join(output_path, f"{file_name_without_ext}_{frame_number}.jpg")

    # Construct FFmpeg command
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f"select='eq(n\,{frame_number})'",
        '-vframes', '1',
        output_path
    ]

    # Execute the command
    subprocess.run(cmd, shell=True)
    print(f"Frame saved to {output_path}")

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Extract a frame from a video.')
    parser.add_argument('video_path', type=str, help='Path to the video file.')
    parser.add_argument('-f', '--frame', type=int, required=True, help='Frame number to extract.')
    parser.add_argument('-o', '--output', type=str, help='Output path for the extracted frame.')
    args = parser.parse_args()

    # Extract the frame
    extract_frame(args.video_path, args.frame, args.output)

if __name__ == "__main__":
    main()

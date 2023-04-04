'''
This python script created to generate flipbook from houdini and convert the output to mp4 video
no worries about color space, what you see in viewport will be ouptut.
Created by: Ayman Abolila: https://about.me/ayman.abolila
Created date: 4/4/2023
'''


import os
import subprocess
import tempfile

# Define directories
temp_dir = tempfile.gettempdir()
input_path = hou.text.expandString('$HIP')+'/flipbook/'
if not os.path.exists(input_path):
    os.makedirs(input_path)
version = str(len(os.listdir(input_path))+1)
video_name = hou.text.expandString('$HIPNAME') + f'_{version}'
video_path = input_path + video_name + '.mp4'
frame_padding = 1
jpg_path = f'{temp_dir}/flipbook/{video_name}_$F{frame_padding}.jpg'

# Fetch data from hou.session if exists
try:
    start_frame = hou.session.start_frame
    end_frame = hou.session.end_frame
    all_viewports = hou.session.all_viewports
except:
    start_frame = '$FSTART'
    end_frame = '$FEND'
    all_viewports = '0'

first_frame = int(hou.text.expandString(start_frame))
end_frame = int(hou.text.expandString(end_frame))
frame_rate = int(hou.text.expandString('$FPS'))


# Create JPG sequnce
cur_desktop = hou.ui.curDesktop()
scene_viewer = hou.paneTabType.SceneViewer
scene = cur_desktop.paneTabOfType(scene_viewer)
scene.flipbookSettings().stash()
flip_book_options = scene.flipbookSettings()

flip_book_options.output(jpg_path)
flip_book_options.renderAllViewports(int(all_viewports))
flip_book_options.useResolution(0)
flip_book_options.frameRange((first_frame, end_frame))
flip_book_options.cropOutMaskOverlay(1)
flip_book_options.outputToMPlay(0)
scene.flipbook(scene.curViewport(), flip_book_options)


# Construct the FFmpeg command
command = [f'{hou.hscriptExpression("$HOUDINI_USER_PREF_DIR")}/scripts/aab_flipbook/script/ffmpeg.exe', '-y',  # Overwrite output file if it already exists
           '-f', 'image2',  # Input format is a sequence of images
           '-start_number',f'{str(first_frame)}',
           '-r', str(frame_rate),  # Set the frame rate
           '-i', f'{temp_dir}/flipbook/{video_name}_%{frame_padding}d.jpg',  # Set the input file pattern
           '-c:v', 'libx264',  # Use the libx264 codec to encode the video
           '-pix_fmt', 'yuv420p',  # Set the pixel format
           '-vf','scale=1920:-2', # Fix Error: "width not divisible by 2"
           video_path]  # Set the output path
          
# Run the FFmpeg command
subprocess.call(command)

if os.path.exists(video_path):
    video_path_print = video_path.replace("/","\\")
    print(f'Successufly generating flipbook to: {video_path_print}')
    
    # Remove temp JPG images
    for frame in range(first_frame, end_frame+1):
        frame_img = f'{temp_dir}/flipbook/{video_name}_{str(frame).zfill(frame_padding)}.jpg'
        if os.path.exists(frame_img):
            os.remove(frame_img)
    
    os.startfile(video_path_print)

else:
    print(f"Can't generate flipbook")


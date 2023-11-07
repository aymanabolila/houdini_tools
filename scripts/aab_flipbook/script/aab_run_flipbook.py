'''
This python script created to generate flipbook from houdini and convert the output to mp4 video
no worries about color space, what you see in viewport will be ouptut.
Created by: Ayman Abolila: https://about.me/ayman.abolila
Created date: 11/7/2023
'''

import hou, json, os, subprocess, tempfile, shutil, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# Define directories
temp_dir = tempfile.gettempdir()
input_path = hou.text.expandString('$HIP')+'/flipbook/'
if not os.path.exists(input_path):
    os.makedirs(input_path)
input_path_bk = hou.text.expandString('$HIP')+'/flipbook/bk/'
if not os.path.exists(input_path_bk):
    os.makedirs(input_path_bk)

mp4_file_count = 1
mp4files = os.listdir(input_path)
for mp4file in mp4files:
    if mp4file.lower().endswith(".mp4"):
        mp4_file_count += 1
version = mp4_file_count

frame_padding = 4

video_name = hou.text.expandString('$HIPNAME') + f'_v{version}'

video_path = input_path + video_name + '.mp4'

jpg_path = f'{temp_dir}/flipbook/{video_name}_$F{frame_padding}.jpg'

settings_file = hou.text.expandString('$HIP')+'/flipbook/settings.txt'

if not os.path.exists(settings_file):
    with open(settings_file, 'w') as file:
        info = {
            'start_frame': '$RFSTART',
            'end_frame': '$RFEND',
            'all_viewports': False,
            'auto_backup': True,
            'comment': True,
            'comment_text': 'Frame: `Frame: $F`',      
                   }
        file.write(json.dumps(info, indent=4))
        
# Fetch data from settings.txt if exists
with open(settings_file, 'r') as file:
    info = json.loads(file.read())
    
    start_frame = info['start_frame']
    end_frame = info['end_frame']
    all_viewports = info['all_viewports']
    auto_backup = info['auto_backup']
    comment = info['comment']
    comment_text = info['comment_text']

first_frame = int(hou.text.expandString(start_frame))
end_frame = int(hou.text.expandString(end_frame))
frame_rate = int(hou.text.expandString('$FPS'))


# Generate comment PNG sequance

font_name = r'C:\Windows\fonts\ariblk_0.ttf'  # Change to the path of your desired font file
font_size = 16


def generate_text_with_shadow(text, font_name, font_size, shadow_color=(0, 0, 0), blur_radius=2):
    # Load the specified font
    if os.path.exists(font_name):
        font = ImageFont.truetype(font_name, font_size)
    else:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))  # Create a temporary image to get text size
    text_width, text_height = draw.textsize(text, font)

    # Calculate the image size to fit the text and shadow
    image_width = text_width + 3 * blur_radius
    image_height = text_height + 3 * blur_radius

    # Create a new image with RGBA mode (transparent background)
    image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))

    # Recreate the font and draw
    if os.path.exists(font_name):
        font = ImageFont.truetype(font_name, font_size)
    else:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(image)

    x = blur_radius
    y = blur_radius

    # Draw the drop shadow
    shadow = Image.new("RGBA", image.size)
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.text((x + blur_radius, y + blur_radius), text, font=font, fill=shadow_color)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    image.paste(shadow, (0, 0), shadow)

    # Draw the text on top of the shadow
    draw.text((x, y), text, font=font, fill=(255, 255, 255))

    return image

# Save the result to a file
if comment:
    for frame in range(end_frame-first_frame+1):
        
        comment_png_path = f'{temp_dir}/flipbook/{video_name}_{str(frame+first_frame).zfill(frame_padding)}.png'
        text = hou.expandStringAtFrame(comment_text, frame+first_frame)
        comment_list = []
        if '\n' in comment_text:
            for line in comment_text.split('\n'):
                text = hou.expandStringAtFrame(line, frame+first_frame)
                
                # Keep only the first two decimal of the float number
                match = re.search(r'(\d+\.\d*)\d*',text)
        
                if match:
                    float_number = match.group(1)
                    formatted_float = str(round(float(float_number),2))
                    text = text.replace(float_number, formatted_float)
                comment_list.append(text)
    
                text = '\n'.join(comment_list)
    
        result_image = generate_text_with_shadow(text, font_name, font_size)
        result_image.save(comment_png_path)

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
camera_node = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer).curViewport().camera()
frame_num = f"'%{{eif\:n+{first_frame}\:d}}'"

    
if camera_node:
    camera = camera_node.name()
    
else:
    camera = ''
    
if comment:
    video_filter = f'drawtext=fontsize=25:fontfile={font_name}:text={camera}:x=(w-tw-10): y=10: fontcolor=white: box=1: boxcolor=0x00000099, scale=1920:-2'
    command = [f'{hou.hscriptExpression("$HOUDINI_USER_PREF_DIR")}/scripts/aab_flipbook/script/ffmpeg.exe', '-y',  # Overwrite output file if it already exists
           '-f', 'image2',  # Input format is a sequence of images
           '-start_number',f'{str(first_frame)}',
           '-framerate', str(frame_rate),  # Set the frame rate
           '-i', f'{temp_dir}/flipbook/{video_name}_%0{frame_padding}d.jpg',  # Set the input file pattern
           '-start_number',f'{str(first_frame)}',
           '-framerate', str(frame_rate),
           '-i', f'{temp_dir}/flipbook/{video_name}_%0{frame_padding}d.png',
           '-filter_complex', f'[0:v][1:v]overlay=x=10:y=10, {video_filter}',  # Adjust overlay parameters
           '-c:v', 'libx264',  # Use the libx264 codec to encode the video
           '-pix_fmt', 'yuv420p',  # Set the pixel format
           '-r', str(frame_rate),
           video_path]  # Set the output path
else:
    video_filter = 'scale=1920:-2'
    command = [f'{hou.hscriptExpression("$HOUDINI_USER_PREF_DIR")}/scripts/aab_flipbook/script/ffmpeg.exe', '-y',  # Overwrite output file if it already exists
           '-f', 'image2',  # Input format is a sequence of images
           '-start_number',f'{str(first_frame)}',
           '-r', str(frame_rate),  # Set the frame rate
           '-i', f'{temp_dir}/flipbook/{video_name}_%{frame_padding}d.jpg',  # Set the input file pattern
           '-c:v', 'libx264',  # Use the libx264 codec to encode the video
           '-pix_fmt', 'yuv420p',  # Set the pixel format
           '-vf', video_filter,
           video_path]  # Set the output path

          
# Run the FFmpeg command
subprocess.call(command)

if os.path.exists(video_path):

    video_path_print = video_path.replace("/","\\")
    print(f'Successufly generating flipbook to: {video_path_print}')
    if auto_backup:
        hou.hipFile.save()
        shutil.copy2(hou.hipFile.name(),input_path_bk + video_name + '.hip')
    # Remove temp JPG images
    for frame in range(first_frame, end_frame+first_frame):
        frame_img = f'{temp_dir}/flipbook/{video_name}_{str(frame).zfill(frame_padding)}.jpg'
        frame_img_png = f'{temp_dir}/flipbook/{video_name}_{str(frame).zfill(frame_padding)}.png'
        if os.path.exists(frame_img):
            os.remove(frame_img)
            if comment:
                os.remove(frame_img_png)
    
    os.startfile(video_path_print)

else:
    print(f"Can't generate flipbook")


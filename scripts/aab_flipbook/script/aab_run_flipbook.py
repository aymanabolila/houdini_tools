'''
This python script created to generate flipbook from houdini and convert the output to mp4 video
no worries about color space, what you see in viewport will be ouptut.
Created by: Ayman Abolila: https://about.me/ayman.abolila
Created date: 18/11/2023
'''

import hou, json, os, subprocess, tempfile, shutil, re, threading
from PIL import Image, ImageDraw, ImageFont, ImageFilter


settings_file = hou.text.expandString('$HIP')+'/flipbook/settings.json'

if not os.path.exists(settings_file):
    with open(settings_file, 'w') as file:
        info = {
                    'video_format': 'mp4',
                    'start_frame': '`$RFSTART`',
                    'end_frame': '`$RFEND`',
                    'all_viewports': False,
                    'auto_backup': True,
                    'comment': True,
                    'font_size': 25,
                    'sys_font_path': 'C:\\Windows\\fonts\\arialbd.ttf',
                    'custom_font': False,
                    'comment_text': '[shotcam]\n`$F`/`$FEND`',
                    'width': 500,
                    'height': 350,
                }
        file.write(json.dumps(info, indent=4))
        
# Fetch data from settings.json if exists
with open(settings_file, 'r') as file:
    info = json.loads(file.read())
    
    video_format = info['video_format'],
    start_frame = info['start_frame']
    end_frame = info['end_frame']
    all_viewports = info['all_viewports']
    auto_backup = info['auto_backup']
    comment = info['comment']
    font_size = info['font_size']
    sys_font_path = info['sys_font_path']
    comment_text = info['comment_text']

video_format = video_format[0]

# Define directories
temp_dir = tempfile.gettempdir()
temp_path = os.path.join(temp_dir,'flipbook')
if not os.path.exists(temp_path):
    os.makedirs(temp_path)

input_path = hou.text.expandString('$HIP')+'/flipbook/'
if not os.path.exists(input_path):
    os.makedirs(input_path)
input_path_bk = hou.text.expandString('$HIP')+'/flipbook/bk/'
if not os.path.exists(input_path_bk):
    os.makedirs(input_path_bk)

video_file_count = 1
videofiles = os.listdir(input_path)
for videofile in videofiles:
    if videofile.lower().endswith(('.mp4')) or videofile.lower().endswith(('.mov')):
        video_file_count += 1
version = video_file_count

video_name = hou.text.expandString('$HIPNAME') + f'_v{version}'

video_path = input_path + video_name + '.' + video_format

jpg_path = '{}/flipbook/{}_$F4.jpg'.format(temp_dir,video_name)

ffmpeg_path = '{}/scripts/aab_flipbook/script/ffmpeg.exe'.format(hou.hscriptExpression("$HOUDINI_USER_PREF_DIR"))

default_font = '{}/scripts/aab_flipbook/arialbd.ttf'.format(hou.hscriptExpression("$HOUDINI_USER_PREF_DIR"))

if not os.path.exists(ffmpeg_path):
    ffmpeg_path = 'ffmpeg'
   

first_frame = int(hou.text.expandString(start_frame))
end_frame = int(hou.text.expandString(end_frame))
frame_rate = int(hou.text.expandString('$FPS'))

def is_font_file(filename):
    return filename.lower().endswith(('.ttf', '.otf')) and os.path.isfile(filename)


# Generate comment PNG sequance

font_name = sys_font_path  # Change to the path of your desired font file

# Load the specified font
if not is_font_file(font_name) or not info['custom_font']:
    font_name = default_font

def generate_text_with_shadow(text, font_name, font_size, shadow_color=(0, 0, 0), blur_radius=2):
    
    font = ImageFont.truetype(font_name, font_size)

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
if comment and comment_text:
    camera_node = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer).curViewport().camera()
    if camera_node:
        comment_text = comment_text.replace('[shotcam]', camera_node.name())
    else:
        comment_text = comment_text.replace('[shotcam]\n','')   
           
            
    for frame in range(end_frame-first_frame+1): 
        
        comment_png_path = '{}/flipbook/{}_{}.png'.format(temp_dir,video_name,str(frame+first_frame).zfill(4))
        text = hou.expandStringAtFrame(comment_text, frame+first_frame)
          
        comment_list = []
        if '\n' in comment_text:
            for line in comment_text.split('\n'):
                text = hou.expandStringAtFrame(line, frame+first_frame)
                
                # Keep only the first two decimal of the float number
                match = re.search('(\d+\.\d*)\d*',text)
        
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
    
if video_format == 'mp4':
    encoder = 'libx264'
if video_format == 'mov':
    encoder = 'prores'

if comment and comment_text:

    # Set the directory paths for the background (JPG) and foreground (PNG) sequences
    background_dir = '{}/flipbook/'.format(temp_dir)
    foreground_dir = '{}/flipbook/'.format(temp_dir)
    output_dir = input_path
    output_video_file = video_path
    
    # List image files in both directories
    background_files = [os.path.join(background_dir, file) for file in os.listdir(background_dir) if file.lower().endswith(('.jpg'))]
    foreground_files = [os.path.join(foreground_dir, file) for file in os.listdir(foreground_dir) if file.lower().endswith(('.png'))]
    
    # Sort the image files by their filenames
    background_files.sort()
    foreground_files.sort()
    
    # Define the frame rate (adjust as needed)
    fps = frame_rate
    
    # Function to overlay images and save a single frame
    def overlay_and_save_frame(background_file, foreground_file, output_file):
        background = Image.open(background_file)
        foreground = Image.open(foreground_file)
    
        # Ensure both images have an alpha channel for transparency
        background = background.convert('RGBA')
        foreground = foreground.convert('RGBA')
    
        # Paste the foreground onto the background without resizing
        combined = Image.new('RGBA', background.size)
        combined.paste(background, (0, 0))
        combined.paste(foreground, (10, 10), foreground)
    
        # Save the combined image
        combined.save(output_file)

    # Create a list to store threads
    threads = []
    
    # Multithreaded overlay and save frames
    for i, (background_file, foreground_file) in enumerate(zip(background_files, foreground_files)):
        output_file = os.path.join(background_dir, 'frame_{}.png'.format(str(i).zfill(4)))
        thread = threading.Thread(target=overlay_and_save_frame, args=(background_file, foreground_file, output_file))
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    command = [
        ffmpeg_path,
        "-y",
        "-framerate", str(fps),
        "-i", "{}/frame_%04d.png".format(background_dir),
        "-c:v", encoder,
        "-pix_fmt", 'yuv420p',
        "-vf", "scale=1920:-2",
        video_path
    ]
    result = subprocess.run(command, capture_output=True, text=True)


else:
    video_filter = 'scale=1920:-2'
    command = [ffmpeg_path, '-y',  # Overwrite output file if it already exists
           '-f', 'image2',  # Input format is a sequence of images
           '-start_number', str(first_frame),
           '-r', str(frame_rate),  # Set the frame rate
           '-i', '{}/flipbook/{}_%04d.jpg'.format(temp_dir,video_name),  # Set the input file pattern
           '-c:v', encoder,  # Use the libx264 codec to encode the video
           '-pix_fmt', 'yuv420p',  # Set the pixel format
           '-vf', video_filter,
           video_path]  # Set the output path

          
    # Run the FFmpeg command
    result = subprocess.run(command, capture_output=True, text=True)


if result.returncode == 0:

    video_path_print = video_path.replace("/","\\")
    print('Successufly generating flipbook to: {}'.format(video_path_print))
    if auto_backup:
        hou.hipFile.save()
        shutil.copy2(hou.hipFile.name(),input_path_bk + video_name + '.hip')
    
    # Remove temp JPG images
    for frame in os.listdir(temp_dir+'/flipbook/'):
        os.remove(os.path.join(temp_dir+'/flipbook/'+frame))
    
    os.startfile(video_path_print)

else:
    # Print the error message
    print("FFmpeg Command failed. Error message:")
    print(result.stderr)


# Intro:
Hello, this tool makes your workflow faster! How such a pain if you'd like to export a video from your Houdini viewport, the traditional way is to create the flipbook with MPlay and wait for it for lunch, then export the video as AVI then convert to MP4 or MOV (prores) using Handbrake or Media Encoder.

I came up with a better way to generate flipbooks, it's fast and very handy, and you'll get to use it so quickly.

# Installation guide:
Download the ZIP file [from here](https://github.com/aymanabolila/houdini_tools/releases/download/AAB_flipbook_to_mp4_0.0.4.zip/AAB_flipbook_to_mp4_0.0.4.zip
), extract it then move  the `packages` and `scripts` folders to your Houdini Preference Folder `C:\Users\{USER}\Documents\houdiniXX.X`.

* _Please take a backup from your preferences folder before installing_

# How to use:
After installing, restart Houdini if it's opened, you will find a new menu called `Tools>Run Flipbook>Run` added at the main Houdini menubar or just press `CTRL+SHIFT+F` to start the flipbook,

![image](https://github.com/aymanabolila/houdini_tools/assets/95883280/ac41acdb-0e06-463a-a837-ee41b12f626b)

* You can edit the options by pressing `CTRL+ALT+SHIFT+F` to modify the start frame and end frame, you can type expressions such as `$FSTART` and `$FEND` or type numbers like `1001`, if you change these default settings, it will be saved into the `$HIP/flipbook/settings.json` file so when you restart Houdini you can find the modifications present.

* Comment options can allow you to type your comments on top of the video output by writing HScript expressions, just type it in \` \`, you can change the font file and size as well if needed.

https://github.com/aymanabolila/houdini_tools/assets/95883280/c07aad90-2c6a-4dc6-995b-08158fd94999

* Auto backup option, allows you to save a backup hip file that generated the flipbook video with the same name in `$HIP/flipbook/bk/`

https://github.com/aymanabolila/houdini_tools/assets/95883280/4162dad6-aca2-4273-b3ca-bb57e8dd9ad6

* Feature to choose `.mov` format output for reacher colors and sharper quality

https://github.com/aymanabolila/houdini_tools/assets/95883280/50e63914-8d70-4f68-9cb8-3f3d67faef6a


* Selecting custom font if needed
  

https://github.com/aymanabolila/houdini_tools/assets/95883280/7936b9f3-0944-43a7-900d-d3b9a48760a7


# How it works:
It saves a sequence of JPG images in your temp folder from your viewport baked into any LUTs or color corrections, then it runs FFMPEG.exe _embedded in the installation folder_ command to convert it to MP4 format directly to your `$HIP` Folder 📂 then opens that file with your default video player at your windows and prints to console the output path.
It works by default at SOPs and it can run at the stage context with Houdini GL, Karma, and Karma XPU.

# Requrments:
* Windows OS
* Houdini 19.0 (Python 3+) and higher.

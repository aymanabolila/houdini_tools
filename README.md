[![Video Break Down](https://i.imgur.com/DmPTM3o.jpg)](https://vimeo.com/814534713)

# Intro:
Hello, this tool makes your workflow faster! How such a pain if you'd like to export a video from your Houdini viewport, the traditional way is to create the flipbook with MPlay and wait for it for lunch, then export the video as MOV or AVI then converted to MP4 using Handbrake or Media Encoder.

I came up with a better way to generate flipbooks, it's fast and very handy, and you'll get to use it so quickly.

# Installation guide:
Download the ZIP file and extract it then move the RAR file in your Houdini Preference Folder `C:\Users\{USER}\Documents\houdiniXX.X`, then extract it here and remove the RAR file.

* _Please take a backup from your preferences folder before installing_

# How to use:
After installing, restart Houdini if it's opened, you will find a new menu called `Tools>Run Flipbook>Run` added at the main Houdini menubar or just press `CTRL+SHIFT+F` to start the flipbook,

You can edit the options by pressing `CTRL+ALT+SHIFT+F` to modify the start frame and end frame, you can type expressions such as `$FSTART` and `$FEND` or type numbers like `1001`, if you changed these default settings, it will be saved into the `$HIP` file so when you restart Houdini you can find the modifications present. If you need all viewports to be rendered type 1 in All Viewports

# How it works:
It saves a sequence of JPG images in your temp folder from your viewport baked into any LUTs or color corrections, then it runs FFMPEG.exe _embedded in the installation folder_ command to convert it to MP4 format directly to your `$HIP` Folder 📂 then opens that file with your default video player at your windows and prints to console the output path.
It works by default at SOPs and it can run at the stage context with Houdini GL, Karma, and Karma XPU.

# Requrments:
* Windows OS
* Houdini 19.0 (Python 3+) and higher.

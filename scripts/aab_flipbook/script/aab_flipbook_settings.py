'''
This python script modify setteings related to aab_flipbook_settings.py
Created by: Ayman Abolila: https://about.me/ayman.abolila
Created date: 4/4/2023
'''

try:
    start_frame = hou.session.start_frame
    end_frame = hou.session.end_frame
    all_viewports = hou.session.all_viewports
except:
    start_frame = '$FSTART'
    end_frame = '$FEND'
    all_viewports = '0'

button_idx, values = hou.ui.readMultiInput(
    "Change flipbook default options", ("Start Frame", "End Frame", "All Viewports (0 or 1)"),
    initial_contents=(start_frame, end_frame, all_viewports),
    title="Flipbook Default Options",
    buttons=("OK", "Cancel"),
    default_choice=0, close_choice=1,
)
start_frame = values[0]
end_frame = values[1]
all_viewports = values[2]


hou.setSessionModuleSource(f'start_frame, end_frame, all_viewports = ("{start_frame}", "{end_frame}", "{all_viewports}")')
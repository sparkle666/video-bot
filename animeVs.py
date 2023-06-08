import os
import subprocess
import ffmpeg
import requests
import logging
from dotenv import dotenv_values
from videoAI import download_video_from_url, add_zoom_effect, get_tenor_video_urls
from console import print_border
from helpers import get_os, get_video_data

config = dotenv_values(".env")

TENOR_API = config["TENOR_API"]
CKEY = config["CKEY"]

v_time = 0.5

VIDEO_INTRO_DURATION = 2.3 
VIDEO_OUTRO_DURATION = 4.7

stats = {
  "Strength" : ["Akaza", 0.5],
  "Power" : ["Akaza", 0.5],
  "AP" : ["Sukuna", 0.5],
  "DC" : ["Akaza", 0.5],
  "Skill" : ["Sukuna", 0.5],
  "Endurance" : ["Akaza", 0.5],
  "Martial_Arts" : ["Sukuna", 0.5],
  "WorkRate" : ["Sukuna", 0.5],
  "Skill" : ["Akaza", 0.5],
  "Winner": ["Akaza", 0.5]
}

working_dir = os.getcwd()
# font_dir = f"{working_dir}/fonts"
# if get_os() == "Windows": font_dir = f"{working_dir}\\fonts\\Helvetica.ttf"

# Add the double slash \\ to escape the colon else wont work on ffmpeg
font_dir = 'C\\:/Users/Sparkles/Desktop/Django Tutorials/python_apps/video-bot/fonts/Helvetica.ttf'


V_WIDTH = 1080
V_HEIGHT = 1633

 

def pad_video(videos, width = 1080, height = 1920, isList = False ):
  """  First Trimming to specific start and stop duration, then resize to 1080x1920 and pad bottom with black video, 
  after that encode to same format
  """
  print_border("Scalling videos to 1080x1920")
  
  try:
    splited_video = ""
    
    if isList:
      for video in videos:
        splited_video = video.split('.')[0]
        os.system(f'ffmpeg -hide_banner -i {video}' +
                  f' -vf "scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"' +
                  f' {splited_video}_padded.mp4')     
        return(f"Scaled: {video}_padded.mp4")
    
    splited_video = videos.split('.')[0]
    os.system(f'ffmpeg -hide_banner -i {videos}' +
              f' -vf "scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"' +
              f' {splited_video}_padded.mp4')
    return(f"{splited_video}_padded.mp4")
  
  except Exception as e:
    logging.exception("Error in padding videos")
 
# pad_video("Saitama0.mp4")
      
def split_file_name(filename):
  """ A function that splits a string and returns the first word """
  return f'{filename.split(".")[0]}'


def create_bg_video(video_name = "bg_video.mp4", duration = 5, color = "black", dimension = f"{V_WIDTH}x{V_HEIGHT}"):
  """Creates a blank video for overlaying other videos"""
  
  try:
    os.system(f"ffmpeg -hide_banner -t {duration} -f lavfi -i color=c={color}:s={dimension} " + 
              f"-c:v libx264 -tune stillimage -pix_fmt yuv420p -preset ultrafast {video_name}")
    return f"{video_name}"
 
  except Exception as e:
    logging.exception(e)
    
# create_bg_video(duration = 10)    

def overlay_videos(video1, video2, bg_video = "bg_video.mp4"):
    """" overlaying 2 videos on letsgo.mp4, trimming it and scalling to 1080x1920"""
    
    # check if background video exists
    file1 = split_file_name(video1)
    file2 = split_file_name(video2)
    if os.path.exists(bg_video) == False:
      print("Please rename a video to 'bg_video.mp4' or create a background video", 
            "this will be used for making the overlay. ")
      return
    
    overlay1 = ffmpeg.input(video1).filter("scale", 1080, -1, height = 1633 / 2)
    overlay2 = ffmpeg.input(video2).filter("scale", 1080, -1, height = 1633 / 2 )
    (
    ffmpeg.input(bg_video)
    .overlay(overlay1)
    .overlay(overlay2, x = 0, y = V_HEIGHT / 2)
    .output(f"{file1}_{file2}_Overlayed.mp4")
    .run()
    )  
    return f"{file1}_{file2}_Overlayed.mp4"
 

def add_text_to_video(videos, text, isList = False ):
  """  Centers a text in the middle of a video. Handles just one word at a time."""
    
  try:
    splited_video = ""
    
    if isList:
      for video in videos:
        splited_video = split_file_name(video)
        command = f"""ffmpeg -hide_banner -i {video} \
        -vf "drawtext=text={text}:x=(w-text_w)/2:y=(h-text_h)/2:fontfile={font_dir}:fontsize=90:bordercolor=black:borderw=8:fontcolor=yellow:fontfile={font_dir}" \
        -c:a copy -preset ultrafast {splited_video}_{text}.mp4"""
        os.system(command)
        
        return(f"{splited_video}_{text}.mp4")
    
    splited_video = split_file_name(videos)
    command = f"""ffmpeg -hide_banner -i {videos} \
        -vf "drawtext=text={text}:x=(w-text_w)/2:y=(h-text_h)/2:fontfile={font_dir}:fontsize=90:bordercolor=black:borderw=8:fontcolor=yellow:fontfile={font_dir}" \
        -c:a copy -preset ultrafast {splited_video}_{text}.mp4"""
    os.system(command)
    
    return(f"{splited_video}_{text}.mp4")
  
  except Exception as e:
    logging.exception(e)

# add_text_to_video("Saitama0_Saitama1_Overlayed.mp4", "Rengoku")   

def add_3text_to_video(video_name: str, char_list: list, font_size: int, output_file: str):
  """ Creates an intro video of title overlayed in the center of a video """
  
  char1 = char_list[0]
  char2 = char_list[1]
  
  try:
    command = f""" ffmpeg -hide_banner -i {video_name} -vf "drawtext=text={char1}:x=(w-text_w)/2:y=((h-text_h)/2)-{font_size}:fontfile={font_dir}:fontsize={font_size}:fontcolor=yellow:borderw=8:bordercolor=black,drawtext=text='Vs':x=(w-text_w)/2:y=(h-text_h)/2:fontfile={font_dir}:fontsize={font_size}:fontcolor=yellow:borderw=8:bordercolor=black,drawtext=text={char2}:x=(w-text_w)/2:y=((h-text_h)/2)+{font_size}:fontfile={font_dir}:fontsize={font_size}:fontcolor=yellow:borderw=8:bordercolor=black" -c:a copy -preset ultrafast {output_file}"""
    
    os.system(command)
    return output_file
  
  except Exception as e:
    logging.exception(e)

# add_3text_to_video("Saitama0_Saitama1_Overlayed.mp4", ["Akaza", "Rengoku"], 60, "out1.mp4")




import os
import subprocess
import ffmpeg
import requests
import logging
from dotenv import dotenv_values
from videoAI import download_video_from_url, add_zoom_effect, get_tenor_video_urls

config = dotenv_values(".env")

TENOR_API = config["TENOR_API"]
CKEY = config["CKEY"]



v_time = 0.5
# Tenor API keys and detials


VIDEO_INTRO_DURATION = 2.3 
VIDEO_OUTRO = 1.5
video_outro_ads = 3.0 

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

font_file = '/storage/emulated/0/PyFiles/Helvetica-Bold.ttf'
working_dir = '/storage/emulated/0/PyFiles/GPT'

V_WIDTH = 1080
V_HEIGHT = 1633

 

def format_video_to_1080(videos, start, stop, isList = False ):
  """  First Trimming to specific start and stop duration, then resize to 1080x1920 and pad bottom with black video, 
  after that encode to same format
  """
  
  print_border("Scalling videos to 1080x1920")
  
  try:
    splited_video = ""
    
    if isList:
      for video in videos:
        splited_video = video.split('.')[0]
        os.system(f"ffmpeg -i {splited_video}1080.mp4 -ss 00:00:00.000 -t 00:00:00.500 -vf 'scale=w=1080:h=1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black' {video}New.mp4")
      return(f"Scaled: {video}New.mp4")
    
    splited_video = videos.split('.')[0]
    os.system(f"ffmpeg -i {splited_video}1080.mp4 -ss 00:00:00.000 -t 00:00:00.500 -vf 'scale=w=1080:h=1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black' {videos}New.mp4")
    return(f"{splited_video}1080.mp4")
  
  except Exception as e:
    logging.exception("Error in formating images")
      
  
  
def create_bg_video(video_name = "bg_video.mp4", duration = 60, color = "black", dimension = "1080x1920"):
  """Creates a blank video for overlaying other videos"""
  
  try:
    os.system(f"ffmpeg -t {duration} -f lavfi -i color=c={color}:s={dimension} -c:v libx264 -tune stillimage -pix_fmt yuv420p {video_name}")
    return f"{video_name}"
 
  except Exception as e:
    logging.exception(e)
    
    
def overlay_videos(video1, video2, bg_video = "bg_video.mp4"):
    """" overlaying 2 videos on letsgo.mp4, trimming it and scalling to 1080x1920"""
    
    # check if background video exists
    if os.path.exists(bg_video) == False:
      print("Please rename a video to 'bg_video.mp4' or create a background video this will be used for making the overlay. ")
      return
    
    overlay1 = ffmpeg.input(video1).filter("scale", 1080, -1, height = 1633 / 2)
    overlay2 = ffmpeg.input(video2).filter("scale", 1080, -1, height = 1633 / 2 )
    (
    ffmpeg.input(bg_video)
    .overlay(overlay1)
    .overlay(overlay2, x = 0, y = v_height / 2)
    .output(f"{video1}_{video2}_Overlayed.mp4")
    .run()
    )  
    return f"{video1}_{video2}_Overlayed.mp4"
    
    # Trim video to 0.5 seconds and upscale to avoid problems when concating videos.
    #prepare_video(["overlay1", "okay", "akaza1"])
    
    #print("cleaning up overlay...")
    # removing the old long overlay
    #os.remove("overlay1.mp4")
def add_text_to_video(video, text):
  """ Centers a text in the middle of a video """
  
  try:
    subprocess.run(['ffmpeg', '-i', f'{video}', '-vf', 
                    f"drawtext=text='{text}':fontsize=90:fontfile={font_file}:x=(w-text_w)/2:y=(h-text_h)/2:fontcolor=yellow:bordercolor=black:borderw=8", '-c:a', 'copy', f"{video.split('.')[0]}.mp4"])
    return f"{video.split('.')[0]}.mp4"
  except Exception as e:
    logging.exception(e)
    
    
def center_text_in_video(char1, char2, stats, font_file):
    print("Inside of center_text_in_video function")
    run_video()
    # Loop through each key-value pair in the dictionary
    clip = open("clip.txt", "w+")   
    
    for key, value in stats.items():
        # Get the first index of the value array
        text = value[0]
        duration = value[1]
        # Center the text in the video file using FFmpeg with a yellow font color and black border color
        subprocess.run(['ffmpeg', '-i', 'overlay1New.mp4', '-vf', f"drawtext=text='{key}':fontsize=90:fontfile={font_file}:x=(w-text_w)/2:y=(h-text_h)/2:fontcolor=yellow:bordercolor=black:borderw=8", '-c:a', 'copy', f"{key}.mp4"])
        print(f"Video done: {key}.mp4, {text}: duration: {duration}")
        prepare_video(key)
        
        if text == "Akaza":
          clip.write(f"file '{key}New.mp4' \n")
          clip.write("file 'akaza1New.mp4' \n")
        else:
          clip.write(f"file '{key}New.mp4' \n")
          clip.write("file 'okayNew.mp4' \n")
    clip.close() 
    
    os.system(f"ffmpeg -f concat -i clip.txt -c copy -safe 0 AkazaVsSukunaAgain.mp4")
    
    os.system("ffmpeg -i AkazaVsSukunaAgain.mp4 -c:v libx264 -crf 28 AkazaVsSukunaEncoded.mp4")
    print("cleaning up...")
    
    for key, values in stats.items():
      os.remove(f"{key}.mp4")
      os.remove(f"{key}New.mp4")
      
    
def start():
  pass
        
#run_video()
#center_text_in_video(stats, font_file)
#prepare_video("okay")



# ffmpeg -i input_video.mp4 -ss 00:00:00.000 -t 00:00:00.500 -filter_complex "[0:v]scale=w=1080:h=1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" output_video.mp4
# Probing h and w of video
# ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 akaza1.mp4 
#subprocess.run(['ffmpeg', '-y', '-i', 'overlayNew.mp4', '-vf', f"drawtext=text='{key}':fontsize=90:fontfile={font_file}:x=(w-text_w)/2:y=(h-text_h)/2:fontcolor=yellow:bordercolor=black:borderw=8", '-t', str(duration),'-c:a', 'copy', '-movflags', '+faststart', f"{key}.mp4"])
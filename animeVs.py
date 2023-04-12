import os
import subprocess
import ffmpeg
import requests
import logging


v_time = 0.5
# Tenor API keys and detials

TENOR_API = "AIzaSyAkeksD2Jbb7nWTGrE7FxRogR13tdNJTDM"
ckey = "Tenor-Videos"

video_intro_duration = 2.3 
video_outro = 1.5
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

v_width = 1080
v_height = 1633

def make_intro(video_title, video):
  """ Make a video intro with time and duration"""
  pass
  
def outro(winner):
  """ Add outro to the video"""
  pass

def download_character_videos(anime_char, api_key, ckey, lmt =2):
   """ Downloads character in list from tenor"""
  #res["results"][0]["media_formats"]["mp4"]["url"]
  urls = []
  try:
    print("inside try")
    req = requests.get(
    "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (anime_char, api_key, ckey,  lmt))
    print(req.status_code)
    if req.status_code == 200:
      res = req.json()
      for index in list(range(len(res["results"]))):
        url.append(res["results"][index]["media_formats"]["mp4"]["url"])
        download_video_from_url(anime_char, url)
    # load the GIFs using the urls for the smaller GIF sizes
    else:
      print(f"Error: {req.status_code}... closing")
  except Exception as e:
      logging.exception("Error making requests")

download_character_videos("Saitama", TENOR_API, ckey)  

def download_video_from_url(char_name, url_list):
  """ Download video from url using ffmpeg"""
  print(f"Dowloading videos for character: {char_name}")
  
  for url in url_list:
    os.system(f"ffmpeg -i {url} {char_name}{url_list.index(url)}.mp4")
  return True

def prepare_video(videos):
  print(f"value in videos: {videos}")
  
  print("Scalling videos to 1080x1920")
  if type(videos) == list:
    for video in videos:
    # First Trimming to specific size 0.5 secs, thrn resize to 1080x1920 and padd bottom with black video, after that encode to same format
      os.system(f"ffmpeg -i {video}.mp4 -ss 00:00:00.000 -t 00:00:00.500 -vf 'scale=w=1080:h=1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black' {video}New.mp4")
      
      print(f"Scaled: {video}New.mp4")
      #os.remove(f"{video}.mp4")
  
  elif type(videos) == str:
    os.system(f"ffmpeg -i {videos}.mp4 -ss 00:00:00.000 -t 00:00:00.500 -vf 'scale=w=1080:h=1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black' {videos}New.mp4")
    
    print(os.path.exists(f"{videos}New.mp4"))
 
    print(f"Scaled: {videos}New.mp4")
  else:
    pass

def convert_to_Mp4():
  """Converts a video, gif or list of video to .mp4"""
  
def create_bg_video(video_name = "bg_video", duration = 60, color = "black", dimension = "1080x1920"):
  """Creates a blank video for overlaying other videos"""
  
  os.system(f"ffmpeg -t {duration} -f lavfi -i color=c={color}:s={dimension} -c:v libx264 -tune stillimage -pix_fmt yuv420p {video_name}.mp4")
  
  return [f"{video_name}.mp4", duration, color, dimension]

def overlay_videos(video1, video2, bg_video = "bg_video.mp4"):
    """" overlaying 2 videos on letsgo.mp4, trimming it and scalling to 1080x1920"""
    
    # check if background video exists
    if os.path.exists(bg_video) == False:
      print("Please rename a video to 'bg_video.mp4' or create a background video this will be used for making the overlay. ")
    
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
  
  subprocess.run(['ffmpeg', '-i', f'{video}.mp4', '-vf', f"drawtext=text='{text}':fontsize=90:fontfile={font_file}:x=(w-text_w)/2:y=(h-text_h)/2:fontcolor=yellow:bordercolor=black:borderw=8", '-c:a', 'copy', f"{text}.mp4"])
  
  return f"{text}.mp4"
    
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
        # check if text in stat is akaza, add akaza to line so that compile all stats and winner will be easy
        print(f"Video done: {key}.mp4, {text}: duration: {duration}")
        # make video to 1080x1920 and add New to the video name
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
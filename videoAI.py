import os
import requests
import logging
from dotenv import load_dotenv
from dotenv import dotenv_values
import openai 
from PIL import ImageOps, Image
import requests_cache
import subprocess
from google_images_search import GoogleImagesSearch
from constants import voices
from helpers import resize_, get_video_data, duplicate_file

config = dotenv_values(".env")
openai_org = config["OPENAI_ORG"]
openai_key = config["OPENAI"]
google_key = config["GOOGLE_API"]
google_project_id = config["GOOGLE_PROJECT_ID"]
TENOR_API = config["TENOR_API"]
CKEY = config["CKEY"]
elevenlabs = config["ELEVENLABS"]

# 1.Enter Script, character names. 2. Generate script audio, generate subtitles from script audio 3. Use main character names to make request to tenor for names. 4. For each video, extract 1 frame as jpg. 5. Resize and crop and images. 6. Check the duration of the script audio 7. Generate 3 zoom image as lomg as the duration from audio 8. Blur the zoomed video. 9 Calculate the duration/number of images to get gow much duration to keep picture or videos. 10. Place the images/videos cropped and edited into center of the video. 11. Add audio to video and sync. 12. Add subtitles and encode video. 12. End

# creating a db to store each requested api requests
session = requests_cache.CachedSession("api_callsDB")
  

# Todo: overlay video on top, write main function that connects all.

def main():
    """ Main program to execute rest of the script """
    
    script = load_script()
    title = ""
    if script:
        temp_title = script.get("title").split()
        title = temp_title[0]
        if len(title) >= 2:
            title = temp_title[0] + "_" + temp_title[1]
        keywords = script.get("keywords")
        script_content = script.get("content")
        #audio_voiceover = generate_audio(script_content, title)
        
        #audio_subtitle = convert_audio_to_srt("One.mp3")
        audio_duration = get_video_data("One.mp3", isVideo=False)
        #print(audio_duration.get("duration"))
        keyword_urls = download_character_videos(keywords[0], 2)
        downloaded_videos = download_video_from_url(keywords[0], keyword_urls)
        print(keywords[0], downloaded_videos)
        # Get one frame from a video to use as background blur
        first_video = downloaded_videos.get("videos")[0]
        picture = generate_pic_from_video(first_video)
        if audio_duration > 10:
        	# Get one 
        	zoomed_video = add_zoom_effect(picture, audio_duration)
        
        

def google_download_images(query):
  """ Download Image from Google """
  gis = GoogleImagesSearch(google_key, google_project_id)
  _search_params = {
    'q': query,
    'num': 3,
    'fileType': 'jpg',
  }
  gis.search(search_params=_search_params, path_to_dir =f'{os.getcwd()}/images', custom_image_name = "saitama-pics")


#google_download_images("Saitama colored")  
    
def load_script() -> dict:
  """ Loads a script from a text file called script.txt"""

  title = keywords = script_contents = ""
  
  if not os.path.exists("script.txt"):
    print("Please create a script.txt file and add your script to it...")
    return False
  try:
      with open("script.txt", "r") as f:
        script = f.read()
        if script == "":
          print("Please add contents to your script.txt. Its empty!!")
          return
        # return the cursor to the beginning to enable reading file well
        f.seek(0)
        txt = f.readlines()
      
        title = txt[0].strip("\n")
        keywords = txt[1].strip("\n")
        if title == "" or keywords == "":
          print("Please add a title, keywords and script: using the recommended format.")
          return
        title_index = title.lower().find("title:")
        keyword_index = keywords.lower().find("keywords:")
        script_index = script.lower().find("script:")
        # getting the contents
        script_contents = script[script_index + len("script:"):].strip()
        title = title[title_index + len("title:"):].strip()
        keywords = keywords[keyword_index + len("keywords:"):].strip().split(",")

        return {"title": title, "keywords": keywords, "content": script_contents }
  except Exception as e:
      logging.exception("Error loading script.txt", e)
      
#load_script()

#get_video_data("newkoko.jpg")
  
def overlay_video_in_center(background_video, foreground_video, duration, overlay_name ):
  """ Adds a video or image in the center of another video
  """
  ffmpeg_overlay = f'ffmpeg -i {background_video} -i {foreground_video} -filter_complex "[0:v][1:v]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable=\'between(t,0,{duration})\'" -c:a copy {overlay_name}'
  try:
      os.system(ffmpeg_overlay)
      return True
  except Exception as e:
    print("Error overlaying video...", e)

#overlay_video_in_center("kokovideo.mp4", "saitama1.mp4", 5, "newvideo4.mp4")

def add_border_to_image(image, new_filename, borderwidth =  40, color= "white"):
  """ Adds a border of x length to an image """
  try:
      ImageOps.expand(Image.open(f'{image}'),border=borderwidth,fill=f'{color}').save(f'{new_filename}')
      return new_filename
  except Exception as e:
      logging.exception("Error adding border...", e)

#add_border_to_image("zoomtest.jpg", new_filename = "anotherkoko.jpg")
  
def api_call_hook(endpoint, method, payload = None, headers = None):
  """ 
  makes a API calls 
  """
  
  if method.lower() == "get":
    req = session.get(endpoint, headers = headers)
    if req.status_code == 200:
      print(req.content)
      return req.content
  elif method.lower() == "post":
    req = session.post(endpoint, json = payload, headers = headers)
    if req.status_code == 200 or req.status_code == 201:
      print(req.content, req.reason)
      return req.content
  else:
    return "Request method out of scope..."

def convert_audio_to_srt(audio):
  """ Gets audio, sends to open ai whisper to make translate to srt
  """
  openai.api_key = openai_key
  openai.organization = openai_org
  audio_ = None 
  audio_name = audio.split(".")[0]
  
  if os.path.exists(audio):
    audio_ = open(audio, "rb")
    print("Opened audio file.")
  else:
    raise FileNotFoundError 
    
  try:
      sub = openai.Audio.transcribe("whisper-1", audio_, response_format="srt")
      print("Writing file.")
      f = open(f"{audio_name}.srt","w")
      f.write(sub)
      f.close()
      audio_.close()
      return f"{audio}.srt"
  except Exception as e:
      logging.exception("Error creating file...")
  
  
def add_zoom_effect(picture, time = 10):
  """ Adds a zoom effect to picture """
  if os.path.exists(picture):
    os.system(f'ffmpeg -loop 1 -i {picture} -y -filter_complex "[0]scale=1200:-2,setsar=1:1[out];[out]crop=1200:670[out];[out]scale=8000:-1,zoompan=z=\'zoom+0.001\':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=250:s=1200x670:fps=25[out]" -acodec aac -vcodec libx264 -map "[out]" -map 0:a? -pix_fmt yuv420p -r 25 -t {10} {picture.split(".")[0]}Zoomed.mp4')
    return f"{picture.split('.')[0]}Zoomed.mp4"
  return None

  
def generate_pic_from_video(video: str) -> str:
  """ Generates pic from video"""
  
  os.system(f"ffmpeg -i {video} -vf 'select=eq(n\,0)' -frames:v 1 {video}.jpg")
  
  return f"{video}.jpg"
  
#generate_pic_from_video("zoomtest")

def download_character_videos(anime_char, lmt=2):
    """ Downloads character in list from tenor"""
    urls = []
    try:
        print("inside try")
        req = session.get(
            "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (anime_char, TENOR_API, CKEY, lmt))
        print(req.status_code)
        if req.status_code == 200:
            res = req.json()
            for index in list(range(len(res["results"]))):
                urls.append(res["results"][index]["media_formats"]["mp4"]["url"])
                print(urls)
            return urls
        # load the GIFs using the urls for the smaller GIF sizes
        else:
            print(f"Error: {req.status_code}... closing")
    except Exception as e:
        logging.exception("Error making requests")

  
def download_video_from_url(char_name, url_list):
  """ Download video from url using ffmpeg"""
  print(f"Dowloading videos for character: {char_name}")
  vid = []
  for url in url_list:
    os.system(f"ffmpeg -i {url} {char_name}{url_list.index(url)}.mp4")
    vid.append(f"{char_name}{url_list.index(url)}.mp4")
    print(vid)
  return {"status": True, "videos": vid}

def add_video_blur(video, blur_strength = 6):
  os.system(f"ffmpeg -i {video}.mp4 -vf 'boxblur={blur_strength}:1' output.mp4")
  return True
  
def generate_audio(text, filename):
  """ Todo: Get text count and convert to seconds in audio, will be used to create the video length to match audio
  """
  headers = {"xi-api-key": elevenlabs}
  api_endpoint = "https://api.elevenlabs.io"
  payload = {"text": text}
  print(text)
  try:
      print("inside try block")
      req = session.post(f"{api_endpoint}/v1/text-to-speech/{voices['Antoni']}/stream", headers = headers, json = payload)
      print("making requests")
      if req.status_code == 200:
        print("Saving audio file")
        f = open(f"{filename}.mp3", "wb")
        f.write(req.content)
        f.close()
        return f"{filename}.mp3"
      print("Error making request...", req.reason)
  except Exception as e:
      logging.exception("Error in request", e)
  
def add_audio_to_video(video, audio, trim = False):
  """ Add audio to video and trim the video to length of audio
  """
  if os.path.exists(f"{video}.mp4") and os.path.exists(f"{audio}.mp3"):
    if trim:
      os.system(f"ffmpeg -i {video}.mp4 -i {audio}.mp3 -c:v copy -c:a aac -shortest {video}withaudio.mp4")
    else:
      os.system(f"ffmpeg -i {video}.mp4 -i {audio}.mp3 -c:v copy -c:a aac {video}withaudio.mp4")
    return f"{video}withaudio.mp4"
  print("Either audio or video does not exist in current directory...")

def add_subtitle_to_video(video, subtitle) -> str:
  """ Adds subtitle to a video. Sub color is a hex code written backwards e.g 12fff - fff21 with &H00 constant"""
  
  if os.path.exists(f"{video}.mp4") and os.path.exists(f"{subtitle}.srt"):
    os.system(f"ffmpeg -i {video}.mp4 -vf subtitles={subtitle}.srt:force_style='PrimaryColour=&H0000ffff' {video}subtitle.mp4")
    
    print("Subtitled...")
    return f"{video}subtitle.mp4"
  print("failed")
  return "Path does not exist for video or subtitle"
  

  
# Project: Nairaland audio for Dairy section 
#main()

#add_zoom_effect("anotherkoko.jpg", 10)

res = duplicate_file("anotherkokoZoomed.mp4", 3)
print(res.get("duplicated_files"))

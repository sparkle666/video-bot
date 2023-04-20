import os
import requests
import math
import logging
from dotenv import load_dotenv
from dotenv import dotenv_values
import openai 
from PIL import ImageOps, Image
import requests_cache
import subprocess
from google_images_search import GoogleImagesSearch
from constants import voices
from helpers import resize_, get_video_data, duplicate_file, add_video_to_file, concat_videos_from_file

config = dotenv_values(".env")
openai_org = config["OPENAI_ORG"]
openai_key = config["OPENAI"]
google_key = config["GOOGLE_API"]
google_project_id = config["GOOGLE_PROJECT_ID"]
TENOR_API = config["TENOR_API"]
CKEY = config["CKEY"]
elevenlabs = config["ELEVENLABS"]

OVERLAY_MAX_TIME = 4
# 1.Enter Script, character names. 2. Generate script audio, generate subtitles from script audio 3. Use main character names to make request to tenor for names. 4. For each video, extract 1 frame as jpg. 5. Resize and crop and images. 6. Check the duration of the script audio 7. Generate 3 zoom image as lomg as the duration from audio 8. Blur the zoomed video. 9 Calculate the duration/number of images to get gow much duration to keep picture or videos. 10. Place the images/videos cropped and edited into center of the video. 11. Add audio to video and sync. 12. Add subtitles and encode video. 12. End

# creating a db to store each requested api requests
session = requests_cache.CachedSession("api_callsDB")
  

# Todo: overlay video on top, write main function that connects all.

def main():
    """ Main program to execute rest of the script """
    
    script = load_script()
    title = ""
    video_filename = "clip2.txt"
    final_bg_video = ""
    num_videos = 1
    final_bg_video = None
    
    if script:
        temp_title = script.get("title").split()
        title = temp_title[0]
        print("___Script Exists___")
        if len(title) >= 2:
            title = temp_title[0] + "_" + temp_title[1]
        keywords = script.get("keywords")
        
        script_content = script.get("content")
        if len(script_content) < 30:
        		return "Erorr:: Script content too small..."
        #audio_voiceover = generate_audio(script_content, title)
        print("____Converting script audio to subtitle___")
        #audio_subtitle = convert_audio_to_srt("tats.mp3")
        audio_subtitle = "tats.srt"
        print("____Converted to srt____: ", audio_subtitle)
        print("___Getting audio data___")
        audio_data = get_video_data("tats.mp3", isVideo=False)
        print(audio_data)
        audio_duration = audio_data.get("duration")
        if audio_duration > 10:
        		print("____Audio is > 10 secs___")
        		num_videos = math.ceil(audio_duration/10)
        all_downloaded_videos_filenames = []
        all_downloaded_videos = {}
        # Get total pic to fetch and divide for the number of each keyword
        print("____Calcling Total audio to fetch___")	
        total_video_to_fetch = int(audio_duration//OVERLAY_MAX_TIME)
        total_video_per_keyword = int(total_video_to_fetch // len(keywords))
        print(f"Total video: {total_video_to_fetch} | total_video_per_keyword: {total_video_per_keyword}")
        for counter in range(len(keywords)):
        		#if keywords.split()
        		print(f"___Fetching Urls from tenor___ for: {keywords[counter]}")
        		urls = get_tenor_video_urls(keywords[counter], total_video_per_keyword)
        		print(f"____Downloading Videos___ for: {keywords[counter]}, urls: {urls}")
        		videos_filenames = download_video_from_url(keywords[counter], urls, isList = True)
        	
        		all_downloaded_videos_filenames += videos_filenames.get("videos")
        		print(f"___All Downloaded Videos FileNames for: {keywords[counter]}___  filenames: {all_downloaded_videos_filenames}")
        		#all_downloaded_videos[keywords[counter]] = videos_filenames.get("videos") 
        		
        #print(keywords[0], downloaded_videos)
        # Get one frame from a video to use as background blur
        print("___Done With Downloading Videos For Each Keyword___")
        first_video = all_downloaded_videos_filenames[0]
        #first_video = all_downloaded_videos.get("videos")[0]
        print("___Generating Picture from Video___", first_video)
        picture = generate_pic_from_video(first_video)
        print("___Pic Name___ - ", picture)
        #resized_picture = resize_(picture, "bg_resized.jpg", width = 1200, height = 670)
        # Get number of vidoeos to use as background
        print("____Converting to video with Zoom Effect___")
        zoomed_video = add_zoom_effect(picture)
        print("____Adding Blurred Effect____")
        blurred_video = add_video_blur(zoomed_video)
        print(f"___Duplicating File {num_videos} x times____")
        duplicated_videos = duplicate_file(blurred_video, num_videos)
        
        final_bg_video = blurred_video
        
        if duplicated_videos.get("status"):
        		print("___Adding Video To Clip.txt___")
        		clip_txt_file = add_video_to_file(duplicated_videos.get("duplicated_files"), video_filename)
        		print("___Concating Files From Clip.txt___")
        		final_bg_video = concat_videos_from_file(clip_txt_file)
        print("___Adding Audio to Full Video__")
        full_video_with_audio = add_audio_to_video(final_bg_video, audio_voiceover, trim = True)
        # overlay downloaded videos on top the blured background video
        print("___Overlaying Videos In Center___")
        time_interval = audio_duration / total_video_to_fetch
        # For each loop, increase start by 
        start = 0
        stop = 0
        for index in list(range(total_video_to_fetch)):
        		stop += time_interval
        		start = stop - time_interval
        		overlay_video_in_center(full_video_with_audio, all_downloaded_videos_filenames[index], start, stop, f"finalvideo{index}.mp4")
        		full_video_with_audio = f"finalvideo{index}.mp4"
        print("___Adding Subtitle to Video___")
        subtitled = add_subtitle_to_video(full_video_with_audio, audio_subtitle)
        print("Omo... We throughhhhhh...")	
        

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
      
        title = txt[0].strip("\n").strip()
        keywords = txt[1].strip("\n").strip()
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
        print(title, keywords, script_contents)
				
        return {"title": title, "keywords": keywords, "content": script_contents }
  except Exception as e:
      logging.exception("Error loading script.txt", e)
      
#load_script()

#get_video_data("newkoko.jpg")
  
def overlay_video_in_center(background_video, foreground_video, start, stop, overlay_name ):
  """ Adds a video or image in the center of another video
  """
  ffmpeg_overlay = f'ffmpeg -i {background_video} -i {foreground_video} -filter_complex "[0:v][1:v]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable=\'between(t,{start},{stop})\'" -c:a copy {overlay_name}'
  try:
      os.system(ffmpeg_overlay)
      return True
  except Exception as e:
    print("Error overlaying video...", e)

#overlay_video_in_center("anotherkokoZoomed.mp4", "saitamaSmall.mp4", 0, 2, "shrink.mp4")

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
      return f"{audio_name}.srt"
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
  splitted = video.split(".")
  os.system(f"ffmpeg -i {video} -vf 'select=eq(n\,0)' -frames:v 1 -pattern_type none -s 1200x670 -f image2 {splitted[0]}.jpg")
  
  return f"{splitted[0]}.jpg"
  
#generate_pic_from_video("tatsumaki_colored0.mp4")

def get_tenor_video_urls(anime_char, lmt=2):
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

  
import os

def download_video_from_url(char_name, url_list, isList=False):
    """Download video from url using ffmpeg"""

    new_char_name = char_name
    print(f"Downloading videos for character: {char_name}")
    splitted = char_name.split()

    if len(splitted) >= 2:
        new_char_name = f"{splitted[0]}_{splitted[1]}"

    if not isList:
        os.system(f"ffmpeg -i {url_list} {new_char_name}.mp4")
        return f"{new_char_name}.mp4"

    vid = []

    for url in url_list:
        if not os.path.exists(f"{new_char_name}{url_list.index(url)}.mp4"):
            os.system(f"ffmpeg -i {url} {new_char_name}{url_list.index(url)}.mp4")
            vid.append(f"{new_char_name}{url_list.index(url)}.mp4")
        vid.append(f"{new_char_name}{url_list.index(url)}.mp4")

    return {"status": True, "videos": vid}

#download_video_from_url("tatsmnaki pants", ["https://media.tenor.com/iryou742PKwAAAPo/rushia-uruha-rushia.mp4"], isList = True)

def add_video_blur(video, blur_strength = 6):
  os.system(f"ffmpeg -i {video} -vf 'boxblur={blur_strength}:1' {video.split('.')[0]}_blurred.mp4")
  return f"{video.split('.')[0]}_blurred.mp4"
  
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
  if os.path.exists(f"{video}") and os.path.exists(f"{audio}"):
    if trim:
      os.system(f"ffmpeg -i {video} -i {audio} -c:v copy -c:a aac -shortest {video}withaudio.mp4")
      return f"{video}withaudio.mp4"
    else:
      os.system(f"ffmpeg -i {video} -i {audio} -c:v copy -c:a aac {video}withaudio.mp4")
    return f"{video}withaudio.mp4"
  print("Either audio or video does not exist in current directory...")

def add_subtitle_to_video(video, subtitle) -> str:
  """ Adds subtitle to a video. Sub color is a hex code written backwards e.g 12fff - fff21 with &H00 constant"""
  
  if os.path.exists(f"{video}") and os.path.exists(f"{subtitle}.srt"):
    os.system(f"ffmpeg -i {video} -vf subtitles={subtitle}:force_style='PrimaryColour=&H0000ffff' {video}WithSubtitle.mp4")
    
    print("Subtitled...")
    return f"{video}WithSubtitle.mp4"
  print("failed")
  return "Path does not exist for video or subtitle"
  

  
# Project: Nairaland audio for Dairy section 
main()

#add_zoom_effect("anotherkoko.jpg", 10)

#res = duplicate_file("anotherkokoZoomed.mp4", 3)
#print(res.get("duplicated_files"))

#add_video_blur("anotherkokoZoomed.mp4")
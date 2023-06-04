import os
import sys
import requests
import math
import time
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
from console import *
from helpers import overlay_multiple_images


config = dotenv_values(".env")
openai_org = config["OPENAI_ORG"]
openai_key = config["OPENAI"]
google_key = config["GOOGLE_API"]
google_project_id = config["GOOGLE_PROJECT_ID"]
TENOR_API = config["TENOR_API"]
CKEY = config["CKEY"]
elevenlabs = config["ELEVENLABS"]

OVERLAY_MAX_TIME = 4
VIDEO_WIDTH = 1200 
VIDEO_HEIGHT = 670 
current_dir = os.getcwd()
images_dir = f"{current_dir}/images"
videos_dir = f"{current_dir}/videos"
assets_dir = f"{current_dir}/assets"

session = requests_cache.CachedSession("api_callsDB")
  

# Todo: overlay video on top, write main function that 

def main():
    """ Main program to execute rest of the script """
    ## create images and video directory in current directory
    if not os.path.exists(images_dir):
    	os.mkdir("images")
    	#os.mkdir("videos")
    
    print_logo()
    time.sleep(2)
    # Calculating time of programming running
    # time_start = time.now()
    
    script = load_script()
    title = ""
    video_filename = "clip2.txt"
    final_bg_video = ""
    num_videos = 1
    final_bg_video = None
    if script:
        temp_title = script.get("title").split()
        title = temp_title[0]
        print_border("Script Exists")
        if len(title) >= 2:
            title = temp_title[0] + "_" + temp_title[1]
        keywords = script.get("keywords")
        #print(keywords)
        script_content = script.get("content")
        if len(script_content) < 30:
          print_border("Erorr:: Script content too small...")
          sys.exit(-1)
            
        #audio_voiceover = generate_audio(script_content, title)
        audio_voiceover = "tats.mp3"
        print_rule("Converting script audio to subtitle")
        #audio_subtitle = convert_audio_to_srt("tats.mp3")
        audio_subtitle = "tats.srt"
        print_border(f"Converted to srt : {audio_subtitle}")
        print_rule("Getting audio data")
        audio_data = get_video_data("tats.mp3", isVideo=False)
        audio_duration = audio_data.get("duration")
        
        if audio_duration > 10:
          print_border("Audio is > 10 secs")
          num_videos = math.ceil(audio_duration/10)
        all_downloaded_picture_filenames = []
        all_downloaded_videos = {}
        # Get total pic to fetch and divide for the number of each keyword
        print_rule("Calcing Total Image to fetch")	
        total_video_to_fetch = int(audio_duration//OVERLAY_MAX_TIME)
        total_video_per_keyword = int(total_video_to_fetch // len(keywords))
        print_border(f"Total Images: {total_video_to_fetch} | total_image_per_keyword: {total_video_per_keyword}")
        all_images = google_download_images(keywords, total_video_per_keyword, isList = True)
        
        if all_images:

          first_pic = all_images[0]
          all_images_resized = [add_border_to_image(img, f"{img.split('.')[0]}_resized.jpg") for img in all_images]
          print_rule("Converting Image to video with Zoom Effect")
          picture = resize_(first_pic, f"{first_pic}_resized.jpg", False, VIDEO_WIDTH, VIDEO_HEIGHT)
          zoomed_video = add_zoom_effect(picture)
          print_rule("Adding Blurred Effect")
          blurred_video = add_video_blur(zoomed_video)
          print_border(f"Duplicating File {num_videos} x times")
          duplicated_videos = duplicate_file(blurred_video, num_videos)

          final_bg_video = blurred_video

          if duplicated_videos.get("status"):
            print_border("___Adding Video To Clip.txt___: Duplicated Videos", duplicated_videos.get("duplicated_files") )
            clip_txt_file = add_video_to_file(duplicated_videos.get("duplicated_files"), video_filename)
            print_rule("Concating Files From Clip.txt")
            final_bg_video = concat_videos_from_file(video_filename)
          print_rule("Adding Audio to Full Video")
          full_video_with_audio = add_audio_to_video(final_bg_video, audio_voiceover, trim = True)
          # overlay downloaded videos on top the blured background video
          print_rule("Overlaying Videos In Center")
          time_interval = audio_duration / total_video_to_fetch
        # 	# For each loop, increase start by time time_interval, set back full_video_with_audio to the new index and loop till end
          start = 0 
          stop = 0
          duration_dict = {} # Hold the duration of each video
          for index, image in enumerate(all_images_resized):
              stop += time_interval
              start = stop - time_interval
              duration_dict[image] = {"start": start, 'stop': stop}
          
          overlayed_video = overlay_multiple_images(full_video_with_audio, all_images_resized, duration_dict, f"{title}.mp4")
          print_rule("Adding Subtitle to Video")
          subtitled = add_subtitle_to_video(overlayed_video, audio_subtitle)
          
          # total_time = time_start + time.now()

          # print_border(f'Total time taken: {total_time}')
          print_rule("Omo... We throughhhhhh...")	
        

def google_download_images(query_list: list, num_of_images: int = 3, isList = False) -> bool:
  """ Download Image from Google. Check if query is a list, splits the query to 
  eg : saitama_power to enable a better filename saving format """

  gis = GoogleImagesSearch(google_key, google_project_id)
  _search_params = {
      'q': query_list,
      'num': num_of_images,
      'fileType': 'jpg',
    }

  downloaded_files = []
  
  with console.status("Downloading Images from Google"):
    if isList:
      for index, query in enumerate(query_list):
        save_filename = query
        _search_params['q'] = query
        temp = query.split()
        if len(temp) > 1:
          save_filename = temp[0] + "_" + temp[1]
        gis.search(search_params=_search_params)
        image_urls = [image.url for image in gis.results()]
        
        for index, url in enumerate(image_urls):
          if os.path.exists(f"{save_filename}{index}.jpg"):
            print_border(f"{save_filename}{index}.jpg already exists...")
            downloaded_files.append(f"{save_filename}{index}.jpg")
            continue
          image_content = api_call_hook(url, method = "get")
          file = open(f"{save_filename}{index}.jpg", "wb")
          file.write(image_content)
          file.close()
          downloaded_files.append(f"{save_filename}{index}.jpg")
      print_rule("Done With Downloading images...")
      print(downloaded_files)
      return downloaded_files
    # If image_urls is not a list
    save_filename = query_list.split()[0]
    print_border("Fetching Image...")
    gis.search(search_params=_search_params)
    #image_url = gis.results()[0].url
    image_urls = [image.url for image in gis.results()]
    for index, url in enumerate(image_urls):
      if os.path.exists(f"{save_filename}{index}.jpg"):
        # If file already exists then skip.
        print_border(f"{save_filename}{index}.jpg already exists...")
        downloaded_files.append(f"{save_filename}{index}.jpg")
        continue
      image_content = api_call_hook(url, method = "get")
      with open(f"{save_filename}{index}.jpg", "wb") as f:
        f.write(image_content)
      downloaded_files.append(f"{save_filename}{index}.jpg")
    print_rule("Images Fetched and Saved")
    return True

    
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
        #print(title, keywords, script_contents)
				
        return {"title": title, "keywords": keywords, "content": script_contents }
  except Exception as e:
      logging.exception("Error loading script.txt", e)
      sys.exit(1)
      
#load_script()

#get_video_data("newkoko.jpg")
  
def overlay_video_in_center(background_video, foreground_video, start, stop, overlay_name ):
  """ Adds a video or image in the center of another video
  """
  ffmpeg_overlay = f'ffmpeg -hide_banner -i {background_video} -i {foreground_video} -filter_complex "[0:v][1:v]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable=\'between(t,{start},{stop})\'" -c:a copy {overlay_name}'
  try:
      os.system(ffmpeg_overlay)
      return True
  except Exception as e:
    print("Error overlaying video...", e)

#overlay_video_in_center("anotherkokoZoomed.mp4", "anotherkoko.jpg", 0, 6, "shrink.mp4")
#resize_("tatsumaki_colored0.jpg", "tatsu.jpg", width = 1299, height = 670)

def add_border_to_image(image, new_filename, borderwidth =  12, color= "white"):
  """ Adds a border of x length to an image, resize to 60% of main video width and saves """
  # TODO: Check if image already exist and skip if true
  try:
			height = int(VIDEO_HEIGHT * 0.6)
			width = int(VIDEO_WIDTH * 0.6)
			print(width, height)
			im = Image.open(image)
			im = im.convert("RGB")
			cropped_image = ImageOps.fit(im, (width, height))
			ImageOps.expand(cropped_image, border=borderwidth,fill=f'{color}').save(f'{new_filename}')
			print_border(f"Resized, border added...{new_filename}")
			return new_filename
  except Exception as e:
      logging.exception("Error adding border...", e)

#add_border_to_image("garou.jpg", new_filename = "garounew.jpg")
  
def api_call_hook(endpoint, method, payload = None, headers = None):
  """ 
  makes a API calls 
  """
  
  if method.lower() == "get":
    req = session.get(endpoint, headers = headers)
    if req.status_code == 200:
      #print(req.content)
      return req.content
  elif method.lower() == "post":
    req = session.post(endpoint, json = payload, headers = headers)
    if req.status_code == 200 or req.status_code == 201:
      print(req.content, req.reason)
      return req.content
  else:
    return "Request method out of scope..."

#google_download_images(["Saitama colored", "saitama angry"], isList = True)  

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
		if os.path.exists(f"{picture.split('.')[0]}Zoomed.mp4"):
			return f"{picture.split('.')[0]}Zoomed.mp4"
		os.system(f'ffmpeg -hide_banner -loop 1 -i {picture} -y -filter_complex "[0]scale=1200:-2,setsar=1:1[out];[out]crop=1200:670[out];[out]scale=8000:-1,zoompan=z=\'zoom+0.001\':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=250:s=1200x670:fps=25[out]" -acodec aac -vcodec libx264 -map "[out]" -map 0:a? -pix_fmt yuv420p -r 25 -t {10} {picture.split(".")[0]}Zoomed.mp4')
		return f"{picture.split('.')[0]}Zoomed.mp4"

  
def generate_pic_from_video(video: str) -> str:
  """ Generates pic from video"""
  splitted = video.split(".")
  os.system(f"ffmpeg -hide_banner -i {video} -vf 'select=eq(n\,0)' -frames:v 1 -pattern_type none -s 1200x670 -f image2 {splitted[0]}.jpg")
  resize_(f"{splitted[0]}.jpg", f"{splitted[0]}resized.jpg", width = 1200, height = 670)
  return f"{splitted[0]}resized.jpg"
  
#generate_pic_from_video("Tatsumaki0.mp4")

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

  

def download_video_from_url(char_name, url_list, isList=False):
    """Download video from url using ffmpeg"""

    new_char_name = char_name
    print(f"Downloading videos for character: {char_name}")
    splitted = char_name.split()

    if len(splitted) >= 2:
        new_char_name = f"{splitted[0]}_{splitted[1]}"

    if not isList:
        os.system(f"ffmpeg -hide_banner -i {url_list} {new_char_name}.mp4")
        return f"{new_char_name}.mp4"

    vid = []

    for url in url_list:
        if not os.path.exists(f"{new_char_name}{url_list.index(url)}.mp4"):
            os.system(f"ffmpeg -hide_banner -i {url} {new_char_name}{url_list.index(url)}.mp4")
            #vid.append(f"{new_char_name}{url_list.index(url)}.mp4")
        vid.append(f"{new_char_name}{url_list.index(url)}.mp4")

    return {"status": True, "videos": vid}

#download_video_from_url("tatsmnaki pants", ["https://media.tenor.com/iryou742PKwAAAPo/rushia-uruha-rushia.mp4"], isList = True)

def add_video_blur(video, blur_strength = 6):
	if os.path.exists(video):
		if os.path.exists(f"{video.split('.')[0]}_blurred.mp4"):
			print("Exists...")
			return f"{video.split('.')[0]}_blurred.mp4"
		# os.system(f"ffmpeg -hide_banner -i {video} -vf 'boxblur={blur_strength}:2' {video.split('.')[0]}_blurred.mp4")
		os.system(f'ffmpeg -hide_banner -i {video} -vf "boxblur={blur_strength}:1" {video.split(".")[0]}_blurred.mp4')
		return f"{video.split('.')[0]}_blurred.mp4"
	
# add_video_blur("saitama_colored3Zoomed.mp4")  
def generate_audio(text, filename):
  """ Todo: Get text count and convert to seconds in audio, will be used to create the video length to match audio
  """
  headers = {"xi-api-key": elevenlabs}
  api_endpoint = "https://api.elevenlabs.io"
  payload = {"text": text}
  print(text)
  try:
      print("inside try block")
      req = session.post(f"{api_endpoint}/v1/text-to-speech/{voices['Arnold']}/stream", headers = headers, json = payload)
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
  #  If the video has been generated before but exited due to error, return the previous video
  splitted = video.split(".")
  
  if os.path.exists(f"{splitted[0]}withaudio.mp4"):
    return f"{splitted[0]}withaudio.mp4"
  
  if os.path.exists(f"{video}") and os.path.exists(f"{audio}"):
    if trim:
      os.system(f"ffmpeg -hide_banner -i {video} -i {audio} -c:v copy -c:a aac -shortest {splitted[0]}withaudio.mp4")
      return f"{splitted[0]}withaudio.mp4"
    else:
      os.system(f"ffmpeg -hide_banner -i {video} -i {audio} -c:v copy -c:a aac {splitted[0]}withaudio.mp4")
    return f"{splitted[0]}withaudio.mp4"
  print("Either audio or video does not exist in current directory...")

def add_subtitle_to_video(video : str, subtitle: str) -> str:
  """ Adds subtitle to a video. Sub color is a hex code written backwards e.g 12fff - fff21 with &H00 constant"""
  
  splitted = video.split(".")
  if os.path.exists(f"{video}") and os.path.exists(f"{subtitle}"):
    command = [
    'ffmpeg',
    '-hide_banner',
    '-i', 'One_Punch.mp4',
    '-vf', "subtitles=tats.srt:force_style='PrimaryColour=&H0000ffff'",
    # '-preset ultrafast',
    'One_PunchWithSubtitle.mp4'
    ]
    subprocess.run(command)
    return f"{splitted[0]}WithSubtitle.mp4"
  
  print("failed")
  return "Path does not exist for video or subtitle"
  

# add_subtitle_to_video("One_Punch.mp4", "tats.srt")  
# Project: Nairaland audio for Dairy section 
# main()

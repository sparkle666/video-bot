import os
import requests
import logging
from dotenv import load_dotenv
from dotenv import dotenv_values
import openai 


config = dotenv_values(".env")
openai_org = config["OPENAI_ORG"]
openai_key = config["OPENAI"]

# Todo: convert speech audio to srt subtitles, overlay video on top, write main function that connects all.

audio_file = open("audio.mp3", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)

ffmpeg_overlay = """
ffmpeg -i background.mp4 -i overlay.mp4 -filter_complex \
"[0:v][1:v]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable='between(t,0,overlay_duration)'" \
-c:a copy output.mp4
"""
voices = {'Rachel': '21m00Tcm4TlvDq8ikWAM', 'Domi': 'AZnzlk1XvdvUeBnXmlld', 'Bella': 'EXAVITQu4vr4xnSDxMaL', 'Antoni': 'ErXwobaYiN019PkySvjV', 'Elli': 'MF3mGyEYCl7XYWbV9V6O', 'Josh': 'TxGEqnHWrfWFTfGW9XjX', 'Arnold': 'VR6AewLTigWG4xSOukaG', 'Adam': 'pNInz6obpgDQGcFmaJgB', 'Sam': 'yoZ06aMxZJJ28mfd3POQ'}


def api_call_hook(endpoint, method, payload = None, headers = None):
  """ 
  makes a API calls 
  """
  req = None
  
  if method.lower() == "get":
    req = requests.get(endpoint, headers = headers)
    if req.status_code == 200:
      print(req.content)
      return req.content
  elif method.lower() == "post":
    req = requests.post(endpoint, json = payload, headers = headers)
    if req.status_code == 200 or req.status_code == 201:
      print(req.content, req.reason)
      return req.content
  else:
    return "Request method out of scope..."
  
def convert_audio_to_srt(audio, subtitle_name):
  """ Gets audio, sends to open ai whisper to make translate to srt
  """
  openai.api_key = openai_key
  openai.organization = openai_org
  try:
    print("Converting audio to subtitle")
      sub = openai.Audio.transcribe("whisper-1", audio, response_format="srt")
      print("Writinf file.")
      f = open(f"{subtitle_name}.srt","w+")
      f.write(sub)
      f.close()
      return f"{subtitle_name}.srt"
  except Exception as e:
      logging.exception("Error creating file...")
      return False
  

convert_audio_to_srt()
  
def add_zoom_effect(picture, time = 10):
  """ Adds a zoom effect to video """
  if os.path.exists(picture):
    os.system(f'ffmpeg -loop 1 -i {picture} -y -filter_complex "[0]scale=1200:-2,setsar=1:1[out];[out]crop=1200:670[out];[out]scale=8000:-1,zoompan=z=\'zoom+0.001\':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=250:s=1200x670:fps=25[out]" -acodec aac -vcodec libx264 -map "[out]" -map 0:a? -pix_fmt yuv420p -r 25 -t {10} {picture.split(".")[0]}Video.mp4')
    return f"{picture.split('.')[0]}Video.mp4"
  return None

  
def generate_pic_from_video(video: str) -> str:
  """ Generates pic from video"""
  
  os.system(f"ffmpeg -i {video}.mp4 -vf 'select=eq(n\,0)' -frames:v 1 {video}.jpg")
  
  return f"{video}.jpg"
  
#generate_pic_from_video("zoomtest")

def download_character_videos(anime_char, api_key, ckey, lmt=2):
    """ Downloads character in list from tenor"""
    urls = []
    try:
        print("inside try")
        req = requests.get(
            "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (anime_char, api_key, ckey, lmt))
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
    #os.system(f"ffmpeg -i {url} {char_name}{url_list.index(url)}.mp4")
    vid.append(f"{char_name}{url_list.index(url)}.mp4")
    print(vid)
  return {"status": True, "videos": vid}

def create_video_zoom_blur(video, blur_strength = 6):
  os.system(f"ffmpeg -i {video}.mp4 -vf 'boxblur={blur_strength}:1' output.mp4")
  return True
  
def generate_audio(text):
  """ Todo: Get text count and convert to seconds in audio, will be used to create the video length to match audio
  """
  headers = {"xi-api-key": elevenlabs}
  api_endpoint = "https://api.elevenlabs.io"
  payload = {"text": text}
  print(text)
  try:
      print("inside try block")
      req = requests.post(f"{api_endpoint}/v1/text-to-speech/{voices['Antoni']}/stream", headers = headers, json = payload)
      print("making requests")
      if req.status_code == 200:
        print("Saving audio file")
        f = open(f"{text[0:6]}.mp3", "wb")
        f.write(req.content)
        f.close()
        return f"{text[0:6]}.mp3"
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
  

  
#add_subtitle_to_video("kokozoomwithaudio", "black")
#add_audio_to_video("kokdjdjejozoom", "Greeti")  
#download_character_videos("Saitama", TENOR_API, ckey)
#generate_audio("Greetings!!")
#download_video_from_url("Saitama", ["https://media.tenor.com/HWdSvD9Wg20AAAPo/one-punch-man-ok.mp4", "helss"])



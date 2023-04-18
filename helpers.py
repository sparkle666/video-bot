import subprocess
import os
from PIL import ImageOps, Image
import logging


def get_image_data(image) -> tuple:
  """ Gets all necesary data from image """
  try:
      img = Image.open(image)
      return img.size
  except Exception as e:
  		logging.exception("Failed to get size", e)
 
 def encode_to_H264(videos, extension = "mp4", isList = False):
 	""" Encodes videos to libx264 a fast encoder """
 	encoded_videos = []
 	try:
 			if isList():
 					for video in videos:
 						os.system(f"ffmpeg -i {video} -c:v libx264 {video.split(".")[0]}.{extension}")
 						encoded_videos.append(f"{video.split(".")[0]}.{extension}")
 					return encoded_videos
 			else:
 					os.system(f"ffmpeg -i {videos} -c:v libx264 {videos.split(".")[0]}.{extension}")
 					return f"{videos.split(".")[0]}.{extension}"
 	except Exception as e:
 			logging.exception("Error:: ", e)

def get_video_data(video, isVideo=True) -> dict:
    """ Returns the video duration of a video in seconds """
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", f"{video}"]
    # Run the ffprobe command using subprocess
    try:
        duration = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        if isVideo:
            dimensions_cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", f"{video}"]
            dimensions_output = subprocess.check_output(dimensions_cmd).decode("utf-8").strip().split("x")
            print(dimensions_output)
            width = int(dimensions_output[0])
            height = int(dimensions_output[1])
            return {"duration": float(duration), "dimension": [width, height]}
        return {"duration": float(duration)}
    except subprocess.CalledProcessError as e:
        print("Error:", e.output)



def resize_(image, resized_filename: str, isVideo = False, width = 0, height = 0, x = 0, y = 0) -> bool:
  """ crops a picture on specified bounding box """
  
  if isVideo:
    try: 
        os.system(f"ffmpeg -i input.mp4 -filter_complex \"crop={w}:{h}:{x}:{y}\" {resized_filename}.mp4")
        return True
    except Exception as e:
        print("Error...", e)
  else:
      try:
          # Open the input image
          input_image = Image.open(image)
          converted = input_image.convert("RGB")
          # Crop the image
          cropped_image = converted.resize((width, height))
          # Save the cropped image
          cropped_image.save(f"{resized_filename}")
          print("resized successfully...")
          return True
      except Exception as e:
          print("Error resizing picture", e)
#resize_()

def duplicate_file(filename, amount = 2):
	if os.path.exists(filename):
		splitted_filename = filename.split(".")[0]
		extension = filename.split(".")[1] 
		cloned_files = []
		try:
				original_file = open(filename, "rb")
				print("____Duplicating Files___")
				for num in list(range(amount)):
					duplicate_file = open(f"{splitted_filename}_{num}.{extension}", "wb")
					duplicate_file.write(original_file.read())
					duplicate_file.close()
					cloned_files.append(f"{splitted_filename}_{num}.{extension}")
					original_file.seek(0)
				original_file.close()
				
				return {"status": True, "duplicated_files": cloned_files}
		except Exception as e:
				logging.exception("ERROR:", e)
				
				
def add_video_to_file(list_of_videos, filename):
	""" Adds a list of videos to an ffmpeg compatible text file """
	try:
			txt_file = open(f"{filename}", "w")
			for text in len(list_of_videos):
				txt_file.writelines(f"file {text} \n")
			txt_file.close()
			return filename
	except Exception as e:
		logging.exception("Error:: ", e)
		
def concat_videos_from_file(filename: str, extension = "mp4"):
	""" concat a .txt files into 1 video """
	
	splitted = filename.split(".")
	if not splitted[1] == "txt":
			return False
	try:
			os.system(f"ffmpeg -f concat -safe 0 -i {filename} -c copy {filename}_zipped.{extension}")
			return f"{splitted[0]}_zipped.{extension}"
	except Exception as e:
			logging.extension("Error: ", e)

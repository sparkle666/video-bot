### The working algorithm
- Enter Script, character names. 
- Generate script audio, generate subtitles from script audio 
- Use main character names to make request to tenor for names.
- For each video, extract 1 frame as jpg. 
- Resize and crop and images. 
- Check the duration of the script audio
- Generate 3 zoom image as lomg as the duration from audio 8. Blur the zoomed video. 
- Calculate the duration/number of images to get gow much duration to keep picture or videos. 
- Place the images/videos cropped and edited into center of the video. 
- Add audio to video and sync. 12. Add subtitles and encode video. 
- End
also
## Character VS algorithm
- Download anime character videos 3 each
- Check if they are mp4, else convert to mp4
- Generate the background video.
- Overlay both character videos on the background video.
- Add text to the full overlayed video in center.
- Create the intro of overlayed video with 3 secs duration.
    - Intro => Overlays the title for 2.3s
- Loop through dictionary and add write file for each instance a character wins.
- Concate 3 videos of the winning character
- Add the intro, main video body and the outro together.
- End

 ### Things to DEBUG:
 1. Video not playing during after overlay 
 2. Add the video overlay and image overlay to video 
 3. clean up unnecessary generated videos like zooom, blurred and final video.  
 4. Make subtitles way bigger.
 5. creating a db to store each requested api requests

### TODOS
- Make overlaying of videos more efficient
- Clean up generated files and keep things clean.
- Add upload to youtube feature 
- Add auto ffmpeg download feature
- Add more documentation


### Position a list of images into a video ffmpeg


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
ffmpeg -i final_zippedwithaudio.mp4 -i saitama_angry0_resized.jpg -i saitama_angry1_resized.jpg -i saitama_angry2_resized.jpg \
-filter_complex "[0][1]overlay=x=(W-w)/2:y=(H-h)/2:enable='between(t,0,4)'[v1]; \
[v1][2]overlay=x=(W-w)/2:y=(H-h)/2:enable='between(t,4,8)'[v2]; \
[v2][3]overlay=x=(W-w)/2:y=(H-h)/2:enable='gt(t,8)'[v3]" \
-map "[v3]" -map 0:a out.mp4

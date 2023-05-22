# 1.Enter Script, character names. 
. Generate script audio, generate subtitles from script audio 
3. Use main character names to make request to tenor for names.
4. 4. For each video, extract 1 frame as jpg. 
5.Resize and crop and images. 
6. Check the duration of the script audio
7.Generate 3 zoom image as lomg as the duration from audio 8. Blur the zoomed video. 
9 Calculate the duration/number of images to get gow much duration to keep picture or videos. 
10. Place the images/videos cropped and edited into center of the video. 
11.Add audio to video and sync. 12. Add subtitles and encode video. 
2. End

 Things to DEBUG:
 1. Video not playing during after overlay 
 2. Add the video overlay and image overlay to video 3. clean up unnecessary generated videos like zooom, blurred and final video.  
 4. Make subtitles way bigger.
# creating a db to store each requested api requests

for counter in range(len(keywords)):
        		#if keywords.split()
        		print_rule(f"Fetching Urls from Google for: {keywords[counter]}")
        		urls = get_tenor_video_urls(keywords[counter], total_video_per_keyword)
        		print_rule(f"Downloading Videos for: {keywords[counter]}, urls: {urls}")
        		videos_filenames = download_video_from_url(keywords[counter], urls, isList = True)
        	
        		all_downloaded_videos_filenames += videos_filenames.get("videos")
        		print_border(f"___All Downloaded Videos FileNames for: {keywords[counter]}___  filenames: {all_downloaded_videos_filenames}")
        		#all_downloaded_videos[keywords[counter]] = videos_filenames.get("videos") 
        		
ffmpeg -r 30 -i animation/%04d.png -vcodec libx264 -crf 25 -pix_fmt yuv420p ~/output.mp4
ffmpeg -framerate 30 -i animation/%04d.png ~/output.gif

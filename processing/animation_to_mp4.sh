ffmpeg -r 30 -i animation/%04d.png -vcodec libx264 -crf 25 -pix_fmt yuv420p ~/output.mp4
ffmpeg -i animation/%04d.png -vf palettegen ~/palette.png
ffmpeg -framerate 30 -start_number 1 -i animation/%04d.png -i ~/palette.png -lavfi paletteuse ~/output.gif

# Chunkify

This script was created to solve a problem I had while using Topaz Video Enhance AI, namely the fact that there is
no easy way to spread the upscaling workload of one video over several GPUs. Henceforth I created this script.
This script allows you to specify the amount of GPUs in your system and evenly spread the upscaling workload of one
video over several GPUs. The way this is done is by separating a video in to chunks and running each chunk on a
different GPU.

## Features
- Divide a video in to chunks to allow for balanced workload distribution.
- Choose whether to concatenate the created chunks back together into a proper video or to keep them separate from
eachother.

## Usage
- -i (Required) <Video input path> - Specify the video to upscale.
- -o <Output name> - Specify the name of the generated video (default is: video).
- -g <GPU count> - Specify the amount of GPUs present on this system (default is 1).
- -s <Scale> - Specify the desired upscaling percentage (100 for 100%, 600 for 600% etc)(default is 200).
- -c - Provide flag to toggle whether to concatenate the created video chunks into one video.
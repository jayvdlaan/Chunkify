import cv2
import os
from concurrent.futures import ThreadPoolExecutor
import sys
import getopt
import subprocess
from numpy import arange
from itertools import repeat
import moviepy.editor as editor

def Worker(a_InputFile, a_OutputFileName, a_Scale, a_FrameChunkCount, a_CurrID, a_TotalFrameCount):
    print("Starting processing on chunk", a_CurrID)
    BeginFrame = a_CurrID * a_FrameChunkCount + 1
    if a_CurrID == 0:
        BeginFrame = 0

    EndFrame = a_FrameChunkCount + (a_FrameChunkCount * a_CurrID)
    if EndFrame + 1 == a_TotalFrameCount:
        EndFrame += 1

    if EndFrame > a_TotalFrameCount:
        EndFrame = a_TotalFrameCount

    Cmd = ('veai.exe -i "' + a_InputFile + '" '
              '-o "' + os.path.dirname(os.path.abspath(a_InputFile)) + '\\' + a_OutputFileName + '_' + str(a_CurrID) + '.mp4" '
              '-f mp4 '
              '-m ghq-1.0.1 '
              '-s ' + str(a_Scale) + ' '
              '-c ' + str(a_CurrID) + ' '
              '-b ' + str(int(BeginFrame)) + ' '
              '-e ' + str(int(EndFrame)))

    Status = subprocess.call(Cmd, shell=True)
    print("Processing finished on chunk", a_CurrID)
    return Status

def Process(a_InputFile, a_OutputFileName, a_Scale, a_GPUCount, a_ConcatenateVids):
    if not os.path.exists('C:\\Program Files\\Topaz Labs LLC\\Topaz Video Enhance AI'):
        print("Topaz Video Enhance AI was not found on your system.")
        return

    os.chdir('C:\\Program Files\\Topaz Labs LLC\\Topaz Video Enhance AI')
    Capture = cv2.VideoCapture(a_InputFile)
    if Capture.isOpened() is False:
        print("Video stream could not be opened.")
        return

    FrameCount = int(Capture.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    print("Video frame count:", FrameCount)

    ChunkSize = float(FrameCount) / a_GPUCount
    ChunkSize = int(abs(ChunkSize))
    print("Chunk processing size:", ChunkSize)

    IDs = arange(0, a_GPUCount)
    print("Executing upscaling, this may take a while...")
    with ThreadPoolExecutor(max_workers=a_GPUCount) as Exec:
        Results = Exec.map(Worker, repeat(a_InputFile), repeat(a_OutputFileName),
                           repeat(a_Scale), repeat(ChunkSize), IDs, repeat(FrameCount))

    Success = True
    for Result in Results:
        if Result != 0:
            Success = False
            break

    if not Success:
        print("Upscaling failed.")
        return
    else:
        print("Upscaling successful")

    if a_ConcatenateVids:
        print("Concatenating chunks into single video file...")
        os.chdir(os.path.dirname(os.path.abspath(a_InputFile)) + '\\')
        Videos = []
        for Index in range(0, a_GPUCount):
            Videos.append(editor.VideoFileClip(a_OutputFileName + '_' + str(Index) + '.mp4'))

        FinalVideo = editor.concatenate_videoclips(Videos)
        FinalVideo.write_videofile(a_OutputFileName + '_' + 'Final.mp4')
        print("Done writing concatenated video file.")
        Input = input("Do you want to delete the chunk clips? (Y/N)")
        if Input == 'Y':
            for Index in range(0, a_GPUCount):
                os.remove(a_OutputFileName + '_' + str(Index) + '.mp4')

    print("Finished.")
    os.system('pause')

def Main(a_Args):
    try:
        Options, Arguments = getopt.getopt(a_Args, "h:i:o:g:s:c:")
    except getopt.GetoptError:
        print("Chunkify.py -h for instructions")
        return

    if len(Options) == 0:
        print("Chunkify.py -h for instructions")
        return

    ReqOptionCheck = False
    OutName = "video.mkv"
    GPUCount = 1
    Scale = 2.0
    InPath = ""
    ConcatenateVid = False
    for Option, Argument in Options:
        if Option == "-i":
            ReqOptionCheck = True
            InPath = Argument
        elif Option == "-o":
            OutName = Argument
        elif Option == "-g":
            GPUCount = int(Argument)
        elif Option == "-s":
            Scale = float(Argument) / 100
        elif Option == "-c":
            if Argument == "Y":
                ConcatenateVid = True
        elif Option == "-h":
           print("Chunkify - Evenly divide upscaling workload over multiple GPUs\n"
                 "\n"
                 "-i (Required) <Video input path> - Specify the video to upscale.\n"
                 "-o <Output name> - Specify the name of the generated video (default is video.mkv).\n"
                 "-g <GPU count> - Specify the amount of GPUs present on this system (default is 1).\n"
                 "-s <Scale> - Specify the desired upscaling percentage (100 for 100%, 600 for 600% etc)(default is 200).\n"
                 "-c <Toggle> - Toggle whether to concatenate the created video chunks into one video (Y/N)(default is N).\n")

    if ReqOptionCheck is True:
        Process(InPath, OutName, Scale, GPUCount, ConcatenateVid)
    else:
        print("Chunkify.py -h for instructions")

if __name__ == '__main__':
    Main(sys.argv[1:])


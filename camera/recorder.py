import glob
import signal
from itertools import cycle, dropwhile
from datetime import datetime
from picamera import PiCamera

STOP_RECORDING = False
CAMERA_RES = '720p'
RECORDING_LENGTH = 10  # Length of individual videos
MAX_NUM_FILES = 2000   # Altogether around 5.55 hours of video at max


def generate_filenames():
    # Filename syntax used: NNNN_YYYY-MM-DD_HH-MM-SS.h264
    # where NNNN cycles from 0001 to MAX_NUM_FILES
    existing_files = glob.glob('*.h264')

    if not existing_files:
        count_from = 1
    else:
        count_from = max(int(f.split('_')[0].lstrip('0')) for f in existing_files)
        if count_from == MAX_NUM_FILES:
            count_from = 1

    iterable = dropwhile(lambda x: x < count_from, cycle(xrange(1, MAX_NUM_FILES + 1)))
    for file_id in iterable:
        if STOP_RECORDING:
            break
        yield datetime.now().strftime('{}_%Y-%m-%d_%H-%M-%S.h264'.format(str(file_id).zfill(4)))


def quit_recorder(*args):
    global STOP_RECORDING
    STOP_RECORDING = True


def record(camera):
    for i in camera.record_sequence(generate_filenames()):
        camera.wait_recording(RECORDING_LENGTH)


def main():
    # Register kill and int signal handling
    signal.signal(signal.SIGTERM, quit_recorder)
    signal.signal(signal.SIGINT, quit_recorder)

    camera = PiCamera(resolution=CAMERA_RES)
    record(camera)

    print('Stopped recording, exiting...')


if __name__ == '__main__':
    main()

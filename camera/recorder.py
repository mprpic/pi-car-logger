import os
import glob
import signal
from itertools import cycle, dropwhile
from picamera import PiCamera

STOP_RECORDING = False
CAMERA_RES = '720p'
RECORDING_LENGTH = 10  # Length of individual videos
MAX_NUM_FILES = 2000   # Altogether around 5.55 hours of video at max
FILE_SUFFIX = '.h264'


def generate_filenames():
    working_dir = os.path.dirname(os.path.realpath(__file__))
    existing_files = glob.glob(working_dir + '/*' + FILE_SUFFIX)

    if not existing_files:
        count_from = 1
    else:
        newest_file = max(existing_files, key=os.path.getctime)
        count_from = int(os.path.basename(newest_file).replace(FILE_SUFFIX, '').lstrip('0'))

        if count_from >= MAX_NUM_FILES:
            count_from = 1
        else:
            count_from += 1  # Bump to next available ID after latest file

    iterable = dropwhile(lambda x: x < count_from, cycle(xrange(1, MAX_NUM_FILES + 1)))
    for file_id in iterable:
        if STOP_RECORDING:
            break

        filename = str(file_id).zfill(4) + FILE_SUFFIX
        filename = os.path.join(working_dir, filename)

        yield filename


def quit_recorder(*args):
    global STOP_RECORDING
    STOP_RECORDING = True


def record(camera):
    print('Starting recording...')
    for _ in camera.record_sequence(generate_filenames()):
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

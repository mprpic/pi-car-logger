import io
import os
import glob
import signal
from itertools import cycle, dropwhile
from picamera import PiCamera

STOP_RECORDING = False

CAMERA_RES = '720p'
CAMERA_FRAMERATE = 30

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


class FlushedFileOutput(object):
    def __init__(self, filename):
        self.out_file = io.open(filename, 'wb')

    def write(self, buf):
        self.out_file.write(buf)

    def flush(self):
        self.out_file.flush()
        os.fsync(self.out_file.fileno())

    def close(self):
        self.out_file.close()


def record(camera):
    print('Starting recording...')

    for filename in generate_filenames():
        camera.start_recording(FlushedFileOutput(filename), format='h264')
        camera.wait_recording(RECORDING_LENGTH)
        camera.stop_recording()


def main():
    # Register kill and int signal handling
    signal.signal(signal.SIGTERM, quit_recorder)
    signal.signal(signal.SIGINT, quit_recorder)

    with PiCamera() as camera:
        camera.resolution = CAMERA_RES
        camera.framerate = CAMERA_FRAMERATE
        record(camera)

    print('Stopped recording, exiting...')


if __name__ == '__main__':
    main()

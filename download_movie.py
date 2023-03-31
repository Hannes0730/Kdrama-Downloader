import subprocess
import re
import time

from PyQt5.QtCore import QThread, pyqtSignal


class MovieDownloader(QThread):
    download_finished = pyqtSignal()
    update_progress = pyqtSignal(int)

    def __init__(self, input_file, output_file):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file

    def run(self):
        cmd = f"ffmpeg -i \"{self.input_file}\" -c:v libx264 -movflags +faststart -preset ultrafast -crf 18 \"{self.output_file}\""
        print(cmd)
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True
        )
        duration_re = re.compile(r"Duration:\s*(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+)\.(?P<milliseconds>\d+)")
        time_re = re.compile(r"time=(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+)\.(?P<milliseconds>\d+)")
        duration = None
        while proc.poll() is None:
            line = proc.stdout.readline()
            if line.strip().startswith("Duration:"):
                match = duration_re.search(line)
                if match:
                    hours = int(match.group("hours"))
                    minutes = int(match.group("minutes"))
                    seconds = int(match.group("seconds"))
                    duration = hours * 3600 + minutes * 60 + seconds
            elif line.strip().startswith("frame="):
                match = time_re.search(line)
                if match and duration:
                    hours = int(match.group("hours"))
                    minutes = int(match.group("minutes"))
                    seconds = int(match.group("seconds"))
                    time_elapsed = hours * 3600 + minutes * 60 + seconds
                    percentage = int((time_elapsed / duration) * 100)
                    # print(f"Conversion progress: {percentage:.2f}%")
                    self.update_progress.emit(percentage)
            else:
                print(line.strip())

        self.download_finished.emit()


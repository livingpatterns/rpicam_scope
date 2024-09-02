import subprocess
import os

class Microscope:
    """ Microscope class
    
    A control class for managing a microscope camera connected to a Raspberry Pi. It supports operations 
    such as previewing the camera feed, capturing images, and recording videos. The class automatically 
    adjusts commands and file handling based on the Raspberry Pi model.
    """
    
    def __init__(self):
        """ 
        Initialize the MicroscopeControl class with default settings. 
        """

        self.valid_resolutions = {
            '1': {'resolution': '1332x990', 'max_fps': 120.05, 'aspect': '4:3'},
            '2': {'resolution': '2028x1080', 'max_fps': 50.03, 'aspect': '16:9'},
            '3': {'resolution': '2028x1520', 'max_fps': 40.01, 'aspect': '4:3'},
            '4': {'resolution': '4056x3040', 'max_fps': 10.00, 'aspect': '4:3'}
        }
        self.pi_model = self.get_pi_model()
        print(f"{self.pi_model}")
        
        self.desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        self.preview_process = None

    def get_pi_model(self):
        """
        Extract the Raspberry Pi model from the system properties
        
        Return:
            str: The model of the Raspberry Pi as a string. Returns 'Unknown' if the model cannot be determined.    
        """
        try:
            with open('/proc/device-tree/model', 'r') as file:
                model = file.read()
                return model.strip()
        except FileNotFoundError:
            print("Failed to detect Raspberry Pi model.")
            return "Unknown"

    def start_preview(self, res_key='0'):
        """
        Start the camera preview using rpicam-hello with the selected resolution on GUI

        Params:
            res_key (str): Key to access resolution details from the valid_resolutions dictionary.
        """

        res_details = self.valid_resolutions.get(res_key)
        command = [
            'rpicam-hello',
            '--timeout',
            '0',
            '--width', res_details['resolution'].split('x')[0],
            '--height', res_details['resolution'].split('x')[1]
        ]
        self.preview_process = subprocess.Popen(command)
        print("Starting indefinite camera preview...")

    def stop_preview(self):
        """
        Stop the camera preview if it is currently running.
        """

        if self.preview_process:
            self.preview_process.terminate()
            self.preview_process.wait()
            self.preview_process = None
            print("Camera preview stopped.")

    def capture_image(self, resolution, filename):
        """
        Capture an image using the specified resolution and filename.

        Params:
            resolution (str): Key to access resolution details from the valid_resolutions dictionary to set the resolution of the captured image.
            filename (str): Base filename to which the .jpg extension will be appended before saving.
        """
        res_details = self.valid_resolutions.get(resolution)

        output_path = os.path.join(filename + '.jpg')
        command = [
            'rpicam-still',
            '-o', output_path,
            '--width', res_details['resolution'].split('x')[0],
            '--height', res_details['resolution'].split('x')[1]
        ]
        subprocess.run(command)
        print(f'Image captured and saved to {output_path}')

    def capture_timelapse(self, resolution, interval, duration, filename):
        """Capture a timelapse by taking images at a set interval."""
        res_details = self.valid_resolutions.get(resolution)
        output_path = os.path.join(filename + '_%04d.jpg')
        command = [
            'rpicam-still',
            '-t', str(duration * 1000),
            '--timelapse', str(interval * 1000),
            '-o', output_path,
            '--width', res_details['resolution'].split('x')[0],
            '--height', res_details['resolution'].split('x')[1]
        ]
        subprocess.run(command)
        print(f'Timelapse captured and saved to {save_folder}')

    def record_video(self, resolution, framerate, duration, filename):
        """
        Record a video with specified resolution, framerate, and duration, then save to a specified path. 
        Handles specific tasks for Raspberry Pi 4 such as merging timestamps into the video file.

        Params:
            resolution (str): The resolution key for fetching resolution details from the valid_resolutions dictionary.
            framerate (float or str): Desired framerate for recording the video; if 'default', uses the maximum framerate available for the selected resolution.
            duration (int): Duration for which the video should be recorded, in seconds.
            filename (str): Base filename to which the appropriate video extension will be appended.
        """

        res_details = self.valid_resolutions.get(resolution)
        max_fps = res_details['max_fps']
        # Set framerate to max FPS if not specified
        if framerate is None or float(framerate) > max_fps:
            framerate = max_fps
            
        output_path = os.path.join(filename + self.get_video_extension())
        print(f"Using {framerate} FPS for the resolution {resolution}. Video stored in {output_path}")

        command = self.get_video_command(res_details['resolution'], framerate, duration, output_path)
        subprocess.run(command)
        if 'Raspberry Pi 4' in self.pi_model:
            # Merging .h264 video with timestamp into a .mkv video format
            input_path = output_path
            output_path = input_path.replace('.h264', '.mkv')
            timestamps_path = os.path.join(self.desktop_path, 'timestamps.txt')
            self.convert_to_mkv(input_path, output_path, timestamps_path)
        else:
            print(f'Video recorded and saved to {output_path}')
            
        
        
    def get_video_extension(self):
        """
        Determine the appropriate video file extension based on the Raspberry Pi model being used.

        Return:
            str: Returns video format given the Raspberry Pi model used
        """
        if not 'Raspberry Pi 5' in self.pi_model:
            return '.h264'
        return '.mp4'

    def get_video_command(self, resolution, framerate, duration, output_path):
        """
        Construct the appropriate video recording command based on the Raspberry Pi model.
        This adjusts parameters like framerate, resolution, and duration to fit the capabilities of the device.

        Params:
            resolution (str): The resolution settings string, e.g., '1920x1080'.
            framerate (float): The framerate to be used in the video recording command.
            duration (int): The duration of the video recording in seconds.
            output_path (str): The path where the video file will be saved.

        Return:
            list: A list of command line arguments for subprocess execution to start video recording.
        """
        if 'Raspberry Pi 4' in self.pi_model:
            # Special handling for RPi 4 to conserve timestamps
            timestamp_path = os.path.join(self.desktop_path, 'timestamps.txt')
            return [
                'rpicam-vid', 
                '--framerate', str(framerate),
                '--width', resolution.split('x')[0],
                '--height', resolution.split('x')[1],
                '--save-pts', timestamp_path,
                '-o', output_path,
                '-t', f'{duration}s'
            ]
        elif 'Raspberry Pi 5' in self.pi_model:
            # Direct recording to mp4 for RPi 5
            return [
                'rpicam-vid', 
                '-t', f'{duration}s', 
                '-o', output_path,
                '--width', resolution.split('x')[0],
                '--height', resolution.split('x')[1],
                '--framerate', str(framerate)
            ]

    def convert_to_mkv(self, input_h264_path, output_mkv_path, timestamps_path):
        """
        Convert an .h264 video file to .mkv format using mkvmerge, including timecodes for Raspberry Pi 4.

        Params:
            input_h264_path (str): The path to the .h264 video file to be converted.
            output_mkv_path (str): The path where the .mkv output file should be saved.
            timestamps_path (str): The path to the file containing timestamps to be integrated into the .mkv file.
        """
        mkvmerge_command = [
            'mkvmerge', 
            '-o', output_mkv_path, 
            '--timecodes', f'0:{timestamps_path}',
            input_h264_path
        ]
        subprocess.Popen(mkvmerge_command)
        print(f"Converted to MKV and saved to {output_mkv_path}")

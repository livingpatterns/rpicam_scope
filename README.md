# rpicam_scope

This project is the start of a microscope interface using a Raspberry Pi HQ Camera. 
The goal is to create a user-friendly application that allows users to control the camera for microscopy purposes, 
including capturing images and recording videos with various settings. The software utilizes the rpicam library, 
which is specifically designed for use with Raspberry Pi cameras.

For more information on the rpicam library and its capabilities, refer to the
[official Raspberry Pi camera documentation.](https://www.raspberrypi.com/documentation/computers/camera_software.html)

## Raspberry Pi Setup

Please refer to the [Raspberry Pi Setup Instructions](https://github.com/livingpatterns/LPL_Information/blob/main/Setup_new_RPi.md) for detailed guidance on setting up your Raspberry Pi.

## Installation

### Clone Repository

To get started with this project, you can clone the repository using one of the following methods:

Use the following command to clone the repository to the `lpl` folder using `HTTPS`:
```bash
git clone https://github.com/livingpatterns/rpicam_scope.git
```
or for access via `SSH`:
```bash
git clone git@github.com:livingpatterns/rpicam_scope.git
```
You have now a new folder named `rpicam_scope` wherever you cloned the repository into.

### Installing Project Pre-Requisites
1. **Update your operating system**
Make sure your operating system is up to date by running:
```bash
sudo apt update
sudo apt upgrade
```
2. Next install the rquired packages:

```bash
sudo apt install python3-pyqt5
pip install pyqtconfig
```

### Setting Up the Desktop Application
To create a desktop shortcut for easy access to the application, follow these steps:

1. **Create a Desktop Entry**
Create a new file named `rpicam_scope.desktop` in the Desktop directory:
```bash
cd ~/Desktop
nano rpicam_scope.desktop
```
2. **Add the following content to the `.desktop` file**
```ini
[Desktop Entry]
Version = 1.0
Name = RPiCam
Comment = Launch the RPi Camera Script
Exec = python3 /home/lpl/rpicam_scope/microscope/controlGUI.py
Icon = /home/lpl/rpicam_scope/microscope/icon/app_icon.png
Terminal = false
Type = Application
Categories = Utility;
```
Save and close the file (`Ctrl+X`, then `Y`, then `Enter`).

3. **Make the `.desktop` file executable**
Run the following command to make the desktop entry executable:
```bash
chmod +x ~/Desktop/rpicam_scope.desktop
```

Now you should see an icon on your `Desktop` named `RPiCam`. Double-clicking this icon will run your application.

From here, when you double-click the desktop icon to run the program, a prompt may appear asking whether you want to execute the file. To prevent this prompt from appearing each time, follow these steps:

- **Open the Home Folder:**
  - Navigate to your home directory by opening the file manager.

- **Access Preferences:**
  - In the file manager, go to `Edit > Preferences`.

- **Adjust the Launch Behavior:**
  - In the `General` tab, check the box next to **"Don't ask options on launch executable file."**

After completing these steps, the program will launch directly when you double-click the `RPiCam` desktop icon, without showing the execution prompt.

Alternatively, you can run the software directly from the command line with the following commands:
```bash
cd ~/lpl/rpicam_scope/microscope
python3 controlGUI.py
```
## Usage

_Coming soon..._

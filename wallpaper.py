import os
import colorama
import json
import glob
import opaciter
import math
import random
import mediafile
import subprocess
import shutil

# <config.json>
WALLPAPER_PATH = ""
DEBUG = False
PREFERED_FETCH_TOOL = ""
UI_SCALE_FACTOR = 1
# </config.json>

CURRENT_WALLPAPER_INDEX = 0

def get_wallpapers():
	return glob.glob(WALLPAPER_PATH + "/*.png") + glob.glob(WALLPAPER_PATH + "/*.jpg")  + glob.glob(WALLPAPER_PATH + "/*.mp4") + glob.glob(WALLPAPER_PATH + "/*.mkv")

def load_config():
	global WALLPAPER_PATH, DEBUG, PREFERED_FETCH_TOOL, UI_SCALE_FACTOR

	configObject = json.load(open("config.json", "r"))

	WALLPAPER_PATH = configObject["wallpaper_path"]
	DEBUG = configObject["debug"]
	PREFERED_FETCH_TOOL = configObject["prefered_fetch_tool"]
	UI_SCALE_FACTOR = configObject["ui_scale_factor"]

def stuff_info_render():
	print(colorama.Style.DIM + f"Jānus v2 ({hex(6825)[2:]})".center(os.get_terminal_size().columns) + colorama.Style.NORMAL)

	return 1

def image_render():
	global WALLPAPER_PATH
	global CURRENT_WALLPAPER_INDEX

	image_width = round(os.get_terminal_size().columns * UI_SCALE_FACTOR)
	image_height = round(os.get_terminal_size().lines * UI_SCALE_FACTOR)

	images_path = get_wallpapers()

	media = mediafile.MediaFile(images_path[CURRENT_WALLPAPER_INDEX])

	if media.extension == "mp4" or media.extension == "mkv":
		d = float(subprocess.check_output([
            "ffprobe","-v","error",
            "-show_entries","format=duration",
            "-of","default=noprint_wrappers=1:nokey=1", file
        ], stderr=subprocess.DEVNULL).strip())

		file_name = file[file.rfind("//"):]

		ts = f"{random.random() * d:.2f}"
		subprocess.run([
            "ffmpeg","-ss", ts,
            "-i", file,
            "-frames:v","1",
            "-q:v","2",
            "temp.jpg"
        ])
       
		os.system(f"chafa \"temp.jpg\" --size {width}x{height} --align center")
		os.remove("temp.jpg")

	else:
		os.system(f"chafa \"{images_path[CURRENT_WALLPAPER_INDEX]}\" --size {image_width}x{image_height} --align center")

	return image_height


def info_render():
	files = get_wallpapers()
	media = mediafile.MediaFile(files[CURRENT_WALLPAPER_INDEX])

	previous_image_name = ""
	next_image_name = ""

	if len(media.name) % 2 == 0:
		previous_image_name = "[  ]"
		next_image_name = "[  ]"
	else:
		previous_image_name = "[  ]"
		next_image_name = "[  ]"
	
	current_image_name = ("{  " + media.name + "  }")
	
	if (CURRENT_WALLPAPER_INDEX != (len(files) - 1)):
		next_media = mediafile.MediaFile(files[CURRENT_WALLPAPER_INDEX + 1])
		next_image_name = f"[ {next_media.name} ]"

	if (CURRENT_WALLPAPER_INDEX != 0):
		previous_media = mediafile.MediaFile(files[CURRENT_WALLPAPER_INDEX - 1])
		previous_image_name = f"[ {previous_media.name} ]"

	print()
	print(previous_image_name.center(os.get_terminal_size().columns)[:-14] + "q  " + colorama.Style.NORMAL)
	print(current_image_name.center(os.get_terminal_size().columns)[:-14] + "w 󰆓 " + colorama.Style.NORMAL)
	print(next_image_name.center(os.get_terminal_size().columns)[:-14] + "e  " + colorama.Style.NORMAL)
	print("x 󰗽   ".rjust(os.get_terminal_size().columns))

	return 2

def render():
	offset = 8

	print("\n" * offset, end="")

	available_height = os.get_terminal_size().lines# * UI_SCALE_FACTOR

	available_height -= stuff_info_render()
	available_height -= image_render()
	available_height -= info_render()

	print((available_height - 1 - offset) * "\n", end="") 

def set_wallpaper():
    os.system("killall waybar")
    os.system("killall mpvpaper")
    os.system("killall fmmpeg")

    files = get_wallpapers()

    file = files[CURRENT_WALLPAPER_INDEX]
    extension = file[file.rfind(".") + 1:]

    if (extension == "mp4") or (extension == "mkv") or (extension == "gif"):
        d = float(subprocess.check_output([
            "ffprobe","-v","error",
            "-show_entries","format=duration",
            "-of","default=noprint_wrappers=1:nokey=1", file
        ], stderr=subprocess.DEVNULL).strip())

        file_name = file[file.rfind("//"):]

        ts = f"{random.random() * d:.2f}"  # точка со случайной секундой
        ts_process = subprocess.run(["ffmpeg", "-ss", ts, "-i", file, "-frames:v", "1", "-q:v", "2", "-pix_fmt", "yuvj420p", "-threads", "1", "temp.jpg"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        width = round(lines * UI_SCALE_COEFFICIENT)
        height = round(width / 16 * 9)

        start = f"chafa \"temp.jpg\" --size {width}x{height} --align center"
        os.system(start)

    os.system(f"wal -i {files[CURRENT_WALLPAPER_INDEX]}")
    os.system(f"matugen image {files[CURRENT_WALLPAPER_INDEX]}")
    
    opaciter.process_file("/home/alex/.config/waybar/colors.css")

    subprocess.Popen(["wal-telegram", "--wal", "-g", "-r"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    s = f'mpvpaper "*" -o "vf-add=fps=12:round=near no-audio loop fullscreen no-border video-unscaled=no vf=lavfi=[scale=w=1920:h=1080:force_original_aspect_ratio=increase,crop=1920:1080]" {files[CURRENT_WALLPAPER_INDEX]}'
    subprocess.Popen([s], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.Popen([f"waybar"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    with open("/home/alex/.config/hypr/modus_percae", "w") as f:
        f.write("exec-once = wal -R\n" + "exec-once = " + s)

    if os.path.isfile("temp.jpg"):
        os.remove("temp.jpg")

def input_handle():
	global CURRENT_WALLPAPER_INDEX

	user_input = input()
	if user_input == "x":
		return 0
	elif user_input == "q":
		if CURRENT_WALLPAPER_INDEX == 0:
			CURRENT_WALLPAPER_INDEX = len(get_wallpapers()) - 1
		else:
			CURRENT_WALLPAPER_INDEX -= 1
		return 1
	elif user_input == "w":
		set_wallpaper()
		return 2
	elif user_input == "e":
		if CURRENT_WALLPAPER_INDEX == len(get_wallpapers()) - 1:
			CURRENT_WALLPAPER_INDEX = 0
		else:
			CURRENT_WALLPAPER_INDEX += 1
		return 1

def start_fetch():
    if PREFERED_FETCH_TOOL != "":
        fetch_tools = [
            "fastfetch",
            "neofetch",
            "screenFetch",
            "archey",
            "archey3",
            "archey4",
            "pfetch",
            "ufetch",
            "hardfetch",
            "winfetch",
            "swmfetch",
            "cpufetch",
            "ferris-fetch",
            "fet.sh",
            "afetch",
            "rsfetch",
        ]

        for fetch in fetch_tools:
            if shutil.which(fetch) != None:
                os.system(fetch)
                break
    else:
        os.system(PREFERED_FETCH_TOOL)

def main():
	os.system("clear")
	load_config()

	while True:
		render()

		input_handled = input_handle()

		if input_handled == 0 or input_handled == 2:
			os.system("clear")
			break

	start_fetch()

if __name__ == "__main__":
	main()

#!/usr/bin/python3

"""
Automate audio Extraction from a video file using ffmpeg and python3
Date: 3-2-2021
https://wingxel.github.io/website/index.html
"""

import getopt
import os
import pprint
import subprocess
import sys
from pathlib import Path

from pymediainfo import MediaInfo


def usage() -> None:
	print("""Usage:
-h or --help            This help text.
-f or --file            Files or directories to extract from.
-s or --save            Where to save extracted audio files.
Example main.py  -f /home/user/Music -s /home/user/Music""")


def get_args() -> dict:
	options = {}
	files = []
	try:
		opts, _ = getopt.getopt(sys.argv[1::], "f:s:h", ["file=", "save=", "help"])
		for opt, arg in opts:
			if opt in ["-h", "--help"]:
				usage()
				sys.exit(0)
			if opt in ["-f", "--file"]:
				files.append(arg)
			if opt in ["-s", "--save"]:
				options["save"] = arg
	except getopt.GetoptError as error:
		print(f"An error occurred while getting args : {str(error)}")
	options["files"] = files
	return options


def check_if_video(file_to_check: str) -> bool:
	file_info = MediaInfo.parse(file_to_check)
	for track in file_info.tracks:
		if track.track_type == "Video":
			return True
	return False


def get_media_title(media_name: str) -> str:
	media_info_value = MediaInfo.parse(media_name)
	for track in media_info_value.tracks:
		if track.track_type == "General":
			return track.title
	return ""


def extract(video_file: str, out: str = os.path.join(str(Path.home()), "Music")) -> None:
	# ***
	if not os.path.exists(out):
		try:
			os.makedirs(out)
		except Exception as error:
			print(f"An error occurred while create directory {out} : {str(error)}")
			sys.exit(1)
	# ***
	filename, extension = os.path.splitext(video_file)
	sv = os.path.join(out, (os.path.split(filename)[-1] + ".mp3"))
	if not os.path.exists(sv):
		try:
			subprocess.call(["ffmpeg", "-y", "-i", video_file, sv], stderr=subprocess.STDOUT)
		except Exception as error:
			print(f"(1) An error occurred: {str(error)}")
	else:
		print(f"File ({sv}) already exists")


def all_in_dir(directory: str, save_location: str = "") -> None:
	if os.path.isdir(directory):
		for root, directories, files in os.walk(directory):
			for f in files:
				if check_if_video(os.path.join(root, f)):
					extract(os.path.join(root, f)) if len(save_location) == 0 else extract(os.path.join(root, f), save_location)
	else:
		print(f"(2) {directory} is not a valid directory!")


def use_commandline_args() -> None:
	fs = get_args()
	pprint.pprint(fs)
	try:
		out = fs["save"]
	except Exception as error:
		print(str(error))
		out = os.path.join(str(Path.home()), "Music")
	if len(fs) > 0:
		for line in fs["files"]:
			if os.path.isfile(line):
				if check_if_video(line):
					extract(line, out)
			elif os.path.isdir(line):
				all_in_dir(line, out)
			else:
				print(f"(3) Error processing {line}")
	else:
		usage()


def use_input(input_data: str) -> None:
	if os.path.isfile(input_data):
		if check_if_video(input_data):
			extract(input_data)
	elif os.path.isdir(input_data):
		all_in_dir(input_data)
	else:
		print(f"(4) Error processing {input_data}")


def use_file(file_name: str) -> None:
	def process_f(filename: str) -> None:
		try:
			with open(filename, "r") as data:
				for line_d in data:
					line = str(line_d).strip('\n')
					if os.path.isdir(line):
						all_in_dir(line)
					elif os.path.isfile(line):
						if check_if_video(line):
							extract(line)
					else:
						print(f"(5) Error processing {line}")
		except Exception as error:
			print(f"(6) error occurred: {str(error)}")

	if os.path.exists(file_name):
		process_f(file_name)
	else:
		print(f"(7) Error processing {file_name}")


def main() -> None:
	if len(sys.argv) > 1:
		use_commandline_args()
	elif os.path.isfile("videos.txt"):
		use_file("videos.txt")
	else:
		path_slash_dir = input("Enter a directory or filename: ")
		use_input(path_slash_dir)


if __name__ == "__main__":
	main()

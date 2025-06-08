import os
import humanize

class MediaFile():
	def __init__(self, name, extension, full_path, size):
		self.name = name
		self.extension = extension
		self.full_path = full_path
		self.size = size

	def __init__(self, full_path):
		self.full_path = full_path
		self.name = full_path[full_path.rfind("/") + 1:full_path.rfind(".")]
		self.extension = full_path[full_path.rfind(".") + 1:]
		self.size = humanize.naturalsize(os.path.getsize(full_path))

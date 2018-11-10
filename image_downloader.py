
import os

from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve, install_opener, build_opener


def save_images_from_urls(urls, directory, prefix):
	# Make the directory to which the images will be saved to
	try:
		os.mkdir(directory)
	except FileExistsError:     # In case the folder already exists
		pass

	# Makes sure that the http servers don't think that this script is a web-scraper
	# Some websites will respond with a 403 Forbidden Error otherwise
	opener = build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	install_opener(opener)

	# Iterate over all the URLs
	for i, url in enumerate(urls):
		try:
			# Images are distinguished by a 5 digit zero-padded id
			urlretrieve(url, '{0:s}{1:s}_{2:05d}.png'.format(directory, prefix, i + 1))
		except (HTTPError, URLError):
			# If for some reason we fail to download an image, ignore and continue
			pass


def dl_image_from_google(search, directory='F:/Images/'):
	pass


if __name__ == '__main__':
	print("Hello Scrapers!")

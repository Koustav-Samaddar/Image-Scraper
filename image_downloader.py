
import os
import re
import time

from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve, install_opener, build_opener, Request, urlopen


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
	# Building url - not using url builder, since the query parameters here are trivial
	query = f"https://www.google.com/search?tbm=isch&q={search}&oq={search}"

	# Makes sure that Google doesn't think that this script is a web-scraper
	# Google will respond with a 403 Forbidden Error otherwise
	req = Request(query, headers={'User-Agent': 'Mozilla/5.0'})
	res = urlopen(req).read()

	# To make debugging easier - otherwise the entire HTML comes in one line
	res = res.decode().replace('><', '>\n<')

	# All image thumbnails show up following the regex below, all other <img> tags are not thumbnails
	f = re.findall(r'<img\sheight="(\d+)"\ssrc="([^"]+)"\swidth="(\d+)"\salt="[^"]+">', res)

	# Getting a list of only the urls - we are keeping other info in f for debugging
	# Also, adding flexibility for future code
	urls = [ url for height, url, width in f ]

	# Downloading the images from the scraped urls into passed directory
	print("Saving images to disk...")
	save_images_from_urls(urls, directory + search + '/', "IMG")

	print(f"{len(f)} images were saved")


if __name__ == '__main__':
	# Testing dl_image_from_google
	print("Starting HTML Scrape from Google Images")
	print()
	tic = time.time()
	dl_image_from_google('kitten')
	toc = time.time()
	print()
	print("Ending HTML Scrape from Google Images")
	print(f"Elapsed time: {toc - tic} seconds")

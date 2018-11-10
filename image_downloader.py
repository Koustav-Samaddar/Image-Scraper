
import os

from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve, install_opener, build_opener


def save_images_from_urls(urls, directory, prefix):
	try:
		os.mkdir(directory)
	except FileExistsError:
		pass

	opener = build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	install_opener(opener)

	for i, url in enumerate(urls):
		try:
			urlretrieve(url, '{0:s}{1:s}_{2:05d}.png'.format(directory, prefix, i + 1))
		except (HTTPError, URLError):
			pass


def dl_image_from_google(search, directory='F:/Images/'):
	pass


if __name__ == '__main__':
	print("Hello Scrapers!")

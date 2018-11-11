
import os
import re
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException

from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve, install_opener, build_opener, Request, urlopen


def save_images_from_urls(urls, directory, prefix, limit=1000):
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
	i = 1
	hist = []
	fail = []
	for url in urls:
		try:
			# Images are distinguished by a 5 digit zero-padded id
			urlretrieve(url, '{0:s}{1:s}_{2:05d}.png'.format(directory, prefix, i + 1))
		except (HTTPError, URLError) as e:
			# If for some reason we fail to download an image, ignore and continue
			fail.append("{0:s}: {1:s}\n".format(type(e).__name__, url))
			continue
		except TimeoutError:
			# If a server takes too long to respond
			fail.append("TimeoutError: {}\n".format(url))
			continue
		except Exception as e:
			# If some unforeseen error were to occur ignore it
			fail.append("{0:s}: {1:s}\n".format(type(e).__name__, url))
			continue
		else:
			# Success! Store this to write to file later and update counter
			hist.append("{0:03d}: {1:s}\n".format(i, url))
			if i >= limit:
				break
			i += 1

	# Write log file with sources of all successful downloads
	with open('{0:s}{1:s}.log'.format(directory, "downloads"), 'w') as f:
		f.writelines(hist)

	# Write log file with sources of all failed downloads and reason (if necessary)
	if len(fail) > 0:
		with open('{0:s}{1:s}.log'.format(directory, "failed"), 'w') as f:
			f.writelines(fail)

	return i


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
	n_imgs = save_images_from_urls(urls, directory + search + '/', "IMG")

	print(f"{n_imgs} images were saved")


def dl_image_from_firefox(search_kw, directory='F:/Images/', limit=1000):
	# Initialise gecko driver with selenium
	driver = webdriver.Firefox()

	# Navigate to Google Image search website
	driver.get("http://images.google.com")

	# Select the image search text field
	search = driver.find_element_by_name('q')

	# Type the query into the search bar
	search.clear()
	search.send_keys(search_kw)
	search.send_keys(Keys.RETURN)

	# Wait for search page to load
	time.sleep(1)

	# Scroll down the page till (hopefully) show more button appears
	body = driver.find_element_by_tag_name('body')
	for i in range(5):
		body.send_keys(Keys.END)
		time.sleep(0.5)

	# Click show more button and wait for rest of the page to load
	btn = driver.find_element_by_id('smb')
	btn.click()
	time.sleep(1)

	# Scroll down till the very end (hopefully) of the page
	for i in range(10):
		body.send_keys(Keys.END)
		time.sleep(0.5)

	# Find all thumbnail image elements
	elems = driver.find_elements_by_class_name('rg_ic')

	# Set to store all big thumbnail image urls
	ret = set()

	print("Finished populating image thumbnails in Google Images")

	# Iterate over each small thumbnail
	for elem in elems:
		elem.click()                                                # Click the small thumbnail
		big_ims = driver.find_elements_by_class_name('irc_mi')      # Get the bigger thumbnails
		try:
			for big_im in big_ims:
				ret.add(big_im.get_attribute('src'))                # Add url to set
		except StaleElementReferenceException:
			pass                                                    # Stop if element expires

		# Only get enough urls to satisfy limit with some heavy redundancy
		if len(ret) > 1.25 * limit:
			break

	print("Finished fetching image urls from larger thumbnails")
	# Stop the Firefox browser instance
	driver.close()
	driver.quit()

	# Filter out Nones from set
	urls = [x for x in ret if x is not None]

	# Download all the images
	n_imgs = save_images_from_urls(urls, directory=directory + search_kw + '/', prefix="IMG", limit=limit)

	print(f"Downloaded {n_imgs} images of {search_kw} from Google Images")


if __name__ == '__main__':
	# Testing dl_image_from_google
	print("Starting HTML Scrape from Google Images")
	print()
	tic = time.time()
	dl_image_from_google('borders')
	toc = time.time()
	print()
	print("Ending HTML Scrape from Google Images")
	print(f"Elapsed time: {toc - tic} seconds")
	print()

	# Testing dl_image_from_firefox
	print("Starting Selenium 'Scrape' from Google Image")
	print()
	tic = time.time()
	dl_image_from_firefox('marble', limit=50)
	toc = time.time()
	print()
	print("Ending Selenium 'Scrape' from Google Image")
	print(f"Elapsed time: {toc - tic} seconds.")

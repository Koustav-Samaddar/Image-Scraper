
import os
import glob

from PIL import Image


def lower_image_resolutions(tgt_size, src_dir, dst_dir):
	"""
	Lowers the resolution and crops into squares all images in src_dir and stores them dst_dir
	:param tgt_size: length of the side of the new square image
	:param src_dir: str -> directory with all un-formatted images
	:param dst_dir: str -> new directory to store semi-formatted images
	:return: None
	"""
	x, y = tgt_size, tgt_size

	# Create destination folder if it doesn't exist already
	try:
		os.mkdir(dst_dir)
	except FileExistsError:
		pass

	# Iterate over files in src_dir
	for src_file in glob.glob(os.path.join(os.path.abspath(src_dir), '*.png')):
		# Separating out file name
		fname, fext = os.path.splitext(src_file)
		fname = fname.split('\\')[-1]

		# Opening image using PIL
		try:
			im = Image.open(src_file)
		except OSError:                 # Image is corrupt or not an actual png
			continue

		# If source image if it's already smaller in one dimension than target size
		w, h = im.size
		if w < x or h < y:
			continue

		# Source image is not a square, a.k.a aspect ratio isn't 1:1
		if w != h:
			# Image aspect ratio is 1:Z where Z > 1, a.k.a image is a tall rectangle
			if w < h:
				# Calculate scaling factor
				scale_factor = x / w

			# Image aspect ratio is Z:1 where Z > 1, a.k.a image is a wide rectangle
			else:   # w > h
				# Calculate scaling factor
				scale_factor = y / h

			# Calculate scaled dimensions
			w *= scale_factor
			h *= scale_factor

			# Normalise dimensions
			w, h = int(round(w)), int(round(h))

			# Resize image
			im = im.resize((int(w), int(h)), Image.LANCZOS)

			# Finding area to be removed to make aspect ratio 1:1
			# We want to crop and keep the center of the image
			if w < h:   # w < h, h > 128
				# Find top and bottom strip of the tall image to remove
				h_start = (h - tgt_size) // 2
				h_end = h - (h - tgt_size + 1) // 2

				# Define the square center of the tall image
				box = (0, h_start, w, h_end)

			else:       # w > h, w > 128
				# Find the left and right strip of the wide image to remove
				w_start = (w - tgt_size) // 2
				w_end = w - (w - tgt_size + 1) // 2

				# Define the square center of the wide image
				box = (w_start, 0, w_end, h)

			# Crop image
			im = im.crop(box)

		# Source image is a square, a.k.a aspect ratio is already 1
		else:
			im.thumbnail((tgt_size, tgt_size), Image.LANCZOS)

		# Save the resized image into the destination folder
		im.save(os.path.join(os.path.abspath(dst_dir), fname) + '.png', 'PNG')


if __name__ == '__main__':
	# Test with images from F:\Images\*
	lower_image_resolutions(128, 'F:/Images/eagle', 'F:/Images/eagle_fmt')

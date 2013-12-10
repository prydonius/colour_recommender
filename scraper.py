#!/usr/bin/env python

# Imaging library
from PIL import Image, ImageDraw
import colorsys

# Scientific clustering library
import scipy
import scipy.misc
import scipy.cluster

# Dribbble API
import dribbble as drib

# Other Libraries
from collections import namedtuple
import cStringIO
import io
import requests
import shutil

palette = namedtuple('Palette', ['dominant', 'others'])

# Set the number of colours we want
COLOUR_PALETTE_SIZE = 5
# Dribbble settings
DRIBBBLE_NUMBER_IMAGES = 200
DRIBBLE_STREAM = "popular"

def getPalette(image):
	array = scipy.misc.fromimage(image)
	shape = array.shape
	array = array.reshape(scipy.product(shape[:2]), shape[2])
	# Use K-Means to get the n most used colours
	colours, dist = scipy.cluster.vq.kmeans(array, COLOUR_PALETTE_SIZE)

	# Get the most dominant colour from this
	vecs, dist = scipy.cluster.vq.vq(array, colours)        
	counts, bins = scipy.histogram(vecs, len(colours))
	index_max = scipy.argmax(counts)                  

	# Remove the dominant from the colours
	colours = colours.tolist()
	if len(colours) == COLOUR_PALETTE_SIZE:
		dominant = colours[index_max]
		del colours[index_max]

		# Return the palette
		p = palette(dominant, colours)
		return p
	else:
		return None

def drawPalette(palette, image):
	# Draw out the palette
	paletteImage = Image.new(image.mode, (20, 140), "white")
	draw = ImageDraw.Draw(paletteImage)
	i=0
	for colour in palette[1]:
		draw.rectangle([(0, i*20),((i+1)*20, (i+1)*20)], fill=tuple(colour))
		i += 1

	# Draw out the dominant colour
	dominant = Image.new(image.mode, (20, 20), "white")
	drawD = ImageDraw.Draw(dominant)
	drawD.rectangle([(0, 0), (20, 20)], fill = tuple(palette[0]))

	# Show the palettes and original image
	dominant.show()
	paletteImage.show()
	image.show()

def convertRGB2HSV(palette):
	HSVPalette = []
	for colour in palette[1]:
		ct = tuple(colour)
		HSVColour = colorsys.rgb_to_hsv(ct[0], ct[1], ct[2])
		HSVPalette.append(HSVColour)

	print HSVPalette

def fetchShots():
	count = 0
	page = 0
	outfile = io.open('dribbble_data', 'w', encoding='utf-8')
	outfile.write(u"title, views, likes, comments, num_shots, followers, dominant, other\n")
	for i in range(0, DRIBBBLE_NUMBER_IMAGES):
		# 50 is the maximum per page
		resp = drib.shots('popular', per_page=50, page=page)
		for shot in resp["shots"]:
			# Get the image and open it
			response = requests.get(shot["image_teaser_url"], stream=True)
			#response = requests.get(shot["image_teaser_url"])
			raw_image = cStringIO.StringIO(response.content)
			img = Image.open(raw_image).convert('RGB')
			palette = getPalette(img)
			print palette
			if palette is not None:
				# Convert to HSV
				#convertRGB2HSV(palette)
				# Get other data
				title = shot["title"]
				views = str(shot["views_count"])
				likes = str(shot["likes_count"])
				comments = str(shot["comments_count"])
				num_shots = str(shot["player"]["shots_count"])
				followers = str(shot["player"]["followers_count"])
				str1 = ''.join(str(e) for e in palette.dominant)
				str2 = ''.join(" ".join(map(str,l)) for l in palette.others)
				outfile.write(title + ", " + views + ", " + likes + ", " + comments + ", " + num_shots + ", " + followers + ", "  + str1 + ", " + str2 + "\n")
		count += 50
		if count >= DRIBBBLE_NUMBER_IMAGES:
			break
		page += 1

if __name__ == "__main__":
	palette = fetchShots()

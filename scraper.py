#!/usr/bin/env python

from PIL import Image, ImageDraw
import scipy
import scipy.misc
import scipy.cluster
from collections import namedtuple

palette = namedtuple('Palette', ['dominant', 'others'])

#Set the number of colours we want
COLOUR_PALETTE_SIZE = 8

def getPalette(image):
	array = scipy.misc.fromimage(image)
	shape = array.shape
	array = array.reshape(scipy.product(shape[:2]), shape[2])

	#Use K-Means to get the n most used colours
	colours, dist = scipy.cluster.vq.kmeans(array, COLOUR_PALETTE_SIZE)

	#Get the most dominant colour from this
	vecs, dist = scipy.cluster.vq.vq(array, colours)        
	counts, bins = scipy.histogram(vecs, len(colours))
	index_max = scipy.argmax(counts)                  

	#Remove the dominant from the colours
	colours = colours.tolist()
	dominant = colours[index_max]
	del colours[index_max]

	#Return the palette
	p = palette(dominant, colours)
	return p

def drawPalette(palette, image):
	print palette
	#Draw out the palette
	paletteImage = Image.new(image.mode, (20, 140), "white")
	draw = ImageDraw.Draw(paletteImage)
	i=0
	for colour in palette[1]:
		draw.rectangle([(0, i*20),((i+1)*20, (i+1)*20)], fill=tuple(colour))
		i += 1

	#Draw out the dominant colour
	dominant = Image.new(image.mode, (20, 20), "white")
	drawD = ImageDraw.Draw(dominant)
	drawD.rectangle([(0, 0), (20, 20)], fill = tuple(palette[0]))

	#Show the palettes and original image
	dominant.show()
	paletteImage.show()
	image.show()


if __name__ == "__main__":
	#Open the image and display 
	image = Image.open("test.jpg")
	#image = Image.open("test2.png")
	palette = getPalette(image)
	drawPalette(palette, image)

from PIL import Image, ImageFont, ImageDraw
import numpy as np
import argparse
import math
import os.path
import tempfile
import shutil
import images2gif

def main():
	parser = argparse.ArgumentParser(
		description='Generate a scrolling gif')
	parser.add_argument('flag', 
		help='The flag, of the form MCA-12345678')
	parser.add_argument('outFile', nargs='?', default='output.gif',
		help='The name of the output file')

	parser.add_argument('-r', '--rebuild', help='Rebuild the base image',
		action='store_true')
	args = parser.parse_args()
	
	#TODO remove debug:
	print args.flag
	binStr = ''
	#Generate a bit string from the flag:
	for char in args.flag:
		binChar = '%08d' % int(bin(ord(char))[2:])
		binStr += binChar

	#TODO remove debug:
	print binStr

	if not os.path.isfile('baseImg.png') or args.rebuild:
		baseImg = genBaseImg(binStr)
		baseImg.save('baseImg.png')
	else:
		baseImg = Image.open('baseImg.png')

	#preview our base image
	#baseImg.show()

	imgWidth, imgHeight = baseImg.size

	#Let's make a tmp directory to hold our frames:
	frameDir = tempfile.mkdtemp()
	 
	#TODO remove debug:
	print frameDir

	#Set how many pixels should change between frames
	frameDelta = 1

	#and fill it with frames:
	framePaths = genFrames(baseImg, frameDir, frameDelta)

	#Now, stitch them together
	decoStitch(framePaths, args.outFile)

	#Clean up:
	#TODO uncomment
	shutil.rmtree(frameDir)


def genBaseImg(binStr):
	#Get our font:
	font = ImageFont.truetype(
		'/usr/share/fonts/truetype/msttcorefonts/times.ttf',
		24)
	#Get our font's dimensions for the bitstring:
	bSize = font.getsize(binStr)
	#Add 10px padding on each side:
	bWidth, bHeight = bSize
	#Compute the margins:
	#wMargin = int(math.ceil(bWidth * 0.1))
	#hMargin = int(math.ceil(bHeight * 0.1))
	wMargin = 10
	hMargin = 10
	
	#Compute the final image size:
	pWidth = bWidth + 2*wMargin
	pHeight = bHeight + 2*hMargin

	pSize = (pWidth, pHeight)

	#Next, actually build the image from scratch:
	baseImg = Image.new('L', pSize, color=(0xFF))

	#Put our text onto the image:
	draw = ImageDraw.Draw(baseImg)
	draw.text((wMargin, hMargin), binStr, font=font, fill=(0))

	return baseImg

def genFrames(baseImg, frameDir, frameDelta):
	'''
	This method generats the sliding scroll frames for the image
	Assumptions:
		The image is wider than it is long
	'''
	imgData = np.array(baseImg)
	height, width = imgData.shape
	if(width < height):
		raise TypeError('Width is greater than height')
	frameSize = (height, height)
	currY = 0
	frameNo = 0
	fPathList = []
	while currY + height < width:
		currFrame = Image.fromarray(
			imgData[:, currY:currY + height])
		#Save frame in directory based on the count:
		frameName = '%05d.png' % frameNo
		framePath = os.path.join(frameDir, frameName)
		currFrame.save(framePath)

		fPathList.append(framePath)

		currY += frameDelta
		frameNo += 1
	return fPathList

def decoStitch(framePaths, outFile):
	imgList = []
	for framePath in framePaths:
		currImg = Image.open(framePath)
		#Add a circle with radius equal to the
		# width of the image:
		#circleImg = Image.new(currImg.mode, currImg.size)
		currArr = np.array(currImg)

		maxX, maxY = currArr.shape
		halfX = maxX / 2
		halfY = maxY / 2

		for i in range(maxX):
			for j in range(maxY):
				rad = ((i - halfX) ** 2 +
					(j - halfY) ** 2)
				rad = math.floor(math.sqrt(rad))
				if rad > halfX - 5:
					currArr[i,j] = 0
		circleImg = Image.fromarray(currArr, currImg.mode)
		#circleImg.save(framePath)
		imgList.append(circleImg)
	images2gif.writeGif(outFile, imgList, duration=.03)

if __name__ == '__main__':
	main()

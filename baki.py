import curses
from curses.textpad import Textbox, rectangle
import sys
import os
import itertools
import time
import shutil

import pygetwindow
import pyautogui
import PIL

import glob
from PIL import Image

print("\nBAKI editor v1.0")
print("type 'baki -h' for help\n")
time.sleep(0.5)

screen = curses.initscr()
curses.start_color()
curses.use_default_colors()

x = 0
y = 0
w = screen.getmaxyx()[1] - 8#160 # 50
h = screen.getmaxyx()[0] - 8#40 # 20
cw = 6#8
ch = 12#16
symb = ""
newsymb = ""
undo_arr = []
undo_counter = 0
shiftMode = 0
fname = "temp.txt"
fileOpened = False
selectionMode = False
sel = []
selection = []
moveMode = -1
global_screen = []
foldername = 'baki_ascii'
animfiles = []
animtime = 0.1
animcount = 5
waitingframes = 30
marquee_h = 10
marquee_w = 50
insertMode = False

def drawSymbol(y, x, symb="#"):
	global screen
	screen.addstr(y, x, symb)
	screen.refresh()

def drawBorder():
	global screen
	global w, h
	str1 = ""
	i = 0
	while i < w + 1:
		str1 = str1 + "-"
		i = i + 1
	screen.addstr(h+1, 0, str1)
	i = 0
	while i < h + 2:
		screen.addstr(i, w+1, "|")
		i = i + 1

	screen.addstr(h+2, 1, "Baki Editor v1.0")
	screen.refresh()

def readFile(fnam):
	global w, h, fname

	try:
		f = open(fnam, 'r', encoding='utf-8')
		lines = f.readlines()
		f.close()
	except:
		print("Error opening file.\n")
		exit()

	w = len(lines[1])-2
	h = len(lines)-1
	fname = fnam

	screen.erase()

	try:
		counter = 0
		for line in lines:
			screen.addstr(counter, 0, line)
			counter = counter + 1
		screen.refresh()

	except:
		print("Error displaying file. File may be too large for current screen size.\n")
		exit()

def saveState():
	global undo_arr, undo_counter
	undo_strs = []
	for i in range(h+1):
		str1 = ""
		for j in range(w+1):
			c = screen.inch(i, j)
			if c == 32:
				c = " "
				str1 = str1 + c
			else:
				c = curses.unctrl(c)
				str1 = str1 + str(c)[2:3]
		undo_strs.append(str1)
	undo_arr.append(undo_strs)
	undo_counter = undo_counter + 1

def unDo():
	global undo_arr, undo_counter
	undo_counter = undo_counter - 1
	if undo_counter < 0:
		undo_counter = 0

	if len(undo_arr) < 1:
		screen.erase()
		drawBorder()
		return

	screen.erase()
	drawBorder()
	counter = 0
	for line in undo_arr[undo_counter]:
		screen.addstr(counter, 0, line)
		counter = counter + 1

	if len(undo_arr) > 0:
		undo_arr.pop()
	if len(undo_arr) > 0:
		undo_arr.pop()
	
	undo_counter = undo_counter - 1
	if undo_counter < 0:
		undo_counter = 0

	screen.refresh()

def printShiftStatus():

	global screen
	global x, y, w, h, symb, shiftMode

	screen.addstr(h+2, w-23, "shiftMode: " + str(shiftMode) + ";")
	screen.refresh()

def printEyeDropper():

	global screen
	global x, y, w, h, symb, shiftMode

	if (symb != ""):
		screen.addstr(h+2, w-27, '"' + symb + '"')
	else:
		screen.addstr(h+2, w-27, '" "')
	screen.refresh()

def deleteString(y):

	global x
	str1 = getEmptyString()
	screen.addstr(y, 0, str1)
	#screen.move(y, x)
	moveCursor(y, x)
	screen.refresh()

def getEmptyString():
	str1 = ""
	for i in range(w+1):
		str1 = str1 + " "
	return str1

def moveStringsUp():

	# get screen contents on y level
	global x, y
	strs_buf = []
	ycounter = y + 1
	while ycounter < h+1:
		str1 = ""
		for j in range(w+1):
			c = screen.inch(ycounter, j)
			if c == 32:
				c = " "
				str1 = str1 + c
			else:
				c = curses.unctrl(c)
				str1 = str1 + str(c)[2:3]

		strs_buf.append(str1)
		ycounter = ycounter + 1

	# clean screen up
	#ycounter = y
	#while ycounter < y: 
	#	screen.addstr(ycounter, 0, getEmptyString())
	#	ycounter = ycounter + 1
	#screen.addstr(h, 0, getEmptyString())
	screen.addstr(h, 0, getEmptyString())

	# move strings up
	counter = 0
	newy = y
	if newy < 0:
		newy = 0
	for line in strs_buf:
		screen.addstr(newy+counter, 0, line)
		counter = counter + 1
	
	screen.refresh()
	#screen.move(newy, x)
	moveCursor(newy, x)

def moveStringsDown():

	# get screen contents on y level
	global x, y
	strs_buf = []
	ycounter = y
	while ycounter <= h-1:
		str1 = ""
		for j in range(w+1):
			c = screen.inch(ycounter, j)
			if c == 32:
				c = " "
				str1 = str1 + c
			else:
				c = curses.unctrl(c)
				str1 = str1 + str(c)[2:3]

		strs_buf.append(str1)
		ycounter = ycounter + 1

	# move strings down
	counter = 0
	newy = y + 1
	screen.addstr(y, 0, getEmptyString())
	if newy >= h:
		newy = h
	for line in strs_buf:
		screen.addstr(newy+counter, 0, line)
		counter = counter + 1
	
	screen.refresh()
	#screen.move(newy, x)
	moveCursor(newy, x)

def moveStringsLeft():

	# get screen contents on y level
	global x, y, w, h
	strs_buf = []
	
	for j in range(h+1):
		str1 = ""
		xcounter = 0
		while xcounter <= x:
			c = screen.inch(j, xcounter)
			if c == 32:
				c = " "
				str1 = str1 + c
			else:
				c = curses.unctrl(c)
				str1 = str1 + str(c)[2:3]
			xcounter = xcounter + 1
		strs_buf.append(str1)
		

	# move strings left
	counter = 0
	for line in strs_buf:
		screen.addstr(counter, 0, line[1:] + " ")
		counter = counter + 1
	
	screen.refresh()
	#screen.move(y, x)
	moveCursor(y, x)

def moveStringsRight():

	# get screen contents on y level
	global x, y, w, h
	strs_buf = []
	
	for j in range(h+1):
		str1 = ""
		xcounter = x
		while xcounter <= w:
			c = screen.inch(j, xcounter)
			if c == 32:
				c = " "
				str1 = str1 + c
			else:
				c = curses.unctrl(c)
				str1 = str1 + str(c)[2:3]
			xcounter = xcounter + 1
		strs_buf.append(str1)
		

	# move strings right
	counter = 0
	for line in strs_buf:
		screen.addstr(counter, x, " " + line)
		counter = counter + 1
	
	drawBorder()
	screen.refresh()
	#screen.move(y, x)
	moveCursor(y, x)

def moveCursor(y, x):
	screen.move(y, x)
	screen.addstr(h+2, w-8, "       ")
	screen.addstr(h+2, w-8, str(x) + ", " + str(y))
	screen.refresh()
	screen.move(y, x)

def setCanvasSize():
	global w, h

	screen.addstr(h+2, 20, "Enter size:")
	screen.refresh()
	editwin = curses.newwin(1, 20, h+2, 32)
	screen.refresh()
	box = Textbox(editwin)
	box.edit()
	message = box.gather()

	strs = getScreen()

	try:
		neww = int(message.split(',')[0])
		newh = int(message.split(',')[1])
		if neww < 1 or newh < 1:
			print("Wrong size. Width or height must be over zero.")
		else:
			w = neww
			h = newh
	except:
		print("Wrong size. Enter two numbers comma separated without spaces.")
		
	screen.erase()
	printContents(resizeContents(strs))
	drawBorder()
	printShiftStatus()
	printEyeDropper()
	screen.refresh()
	#screen.move(y, x)
	moveCursor(y, x)

def getScreen():
	global w, h
	strs = []
	i = 0
	while i <= h:
		str1 = ""
		counter = 0
		while counter < w+1:
			c = screen.inch(i, counter)
			if c == 32:
				c = " "
				str1 = str1 + c
			else:
				c = curses.unctrl(c)
				str1 = str1 + str(c)[2:3]
			counter = counter + 1
		strs.append(str1)
		i = i + 1
	return strs

def printContents(strs):
	counter = 0
	while counter < len(strs):
		screen.addstr(counter, 0, strs[counter])
		counter = counter + 1
	screen.refresh()

def resizeContents(strs):
	global w, h
	strs1 = []
	if h+1 < len(strs):
		while (h < len(strs)-1):
			strs.pop()
			print ("popped")
	for line in strs:
		line1 = line[0:w+1]
		strs1.append(line1)
	return strs1

def printPattern(symbo, size, start_with_symbol):

	global x, y
	if start_with_symbol == True:
		str1 = symbo
	else:
		str1 = ""
	for i in range(size):
		if start_with_symbol:
			str1 = str1 + " " + symbo
		else:
			str1 = str1 + symbo + " "
	screen.addstr(y, x, str1)
	screen.refresh()
	if start_with_symbol == True:
		curx = x + len(str1) + 1
	else:
		curx = x + len(str1)
	if curx > w:
		curx = w
	x = curx
	#screen.move(y, curx)
	moveCursor(y, curx)

def moveColumnUp():
	global y, x, w, h

	strs = getScreen()
	counter = y
	while counter < h:
		if counter + 1 <= h:
			strs[counter] = strs[counter][:x] + strs[counter+1][x] + strs[counter][x+1:]
		counter = counter + 1
	strs[h] = strs[h][:x] + " " + strs[h][x+1:]
	screen.erase()
	printContents(strs)
	drawBorder()
	moveCursor(y, x)

def moveColumnDown():
	global y, x, w, h

	strs = getScreen()
	counter = y
	while counter >= 0:
		if counter - 1 > 0:
			strs[counter] = strs[counter][:x] + strs[counter-1][x] + strs[counter][x+1:]
		counter = counter - 1
	#strs[0] = strs[0][:x] + " " + strs[0][x+1:]
	screen.erase()
	printContents(strs)
	drawBorder()
	moveCursor(y, x)

def replaceSymbolDialog():

	global h, w, screen

	screen.addstr(h+2, 20, "Replace:")
	screen.refresh()
	editwin = curses.newwin(1, 20, h+2, 29)
	screen.refresh()
	box = Textbox(editwin)
	box.edit()
	message = box.gather()

	try:
		s = message.split(',')[0]
		s1 = message.split(',')[1]
		s1 = s1[0]

		newstrs = []
		strs = getScreen()
		for line in strs:
			line1 = ""
			line1 = line.replace(s, s1)
			newstrs.append(line1)

		screen.erase()
		printContents(newstrs)
		drawBorder()
		moveCursor(y, x)

	except:
		print("Replace wrong symbols")
		drawBorder()
		moveCursor(y,x)
		drawBorder()
		screen.refresh()

def deleteColumn():

	global y, x

	strs = getScreen()
	counter = 0
	while counter < h:
		strs[counter] = strs[counter][:x] + " " + strs[counter][x+1:]
		counter = counter + 1
	#strs[h] = strs[h][:x] + " " + strs[h][x+1:]
	screen.erase()
	printContents(strs)
	drawBorder()
	moveCursor(y, x)

def toggleSelectionMode():
	global y, x, selectionMode, sel, selection, global_screen, moveMode

	if selectionMode == False:

		if moveMode > -1:
			moveMode = -1
			moveSelection(False)
			moveCursor(y, x)
			sel = []
			selection = []
			global_screen = []
			return

		if len(selection) > 0 and selectionMode == False:
			dropSelection()

		sel.append([x, y])
		sel.append([x, y])
		global_screen = getScreen()
		selection = getSelectionWithContents(getSelection())
		drawSelection()
		selectionMode = not selectionMode
		moveCursor(y, x)

	else:
		if len(sel) >= 2:
			sel.pop()
		sel.append([x, y])
		selection = getSelectionWithContents(getSelection())
		#print(selection)
		#global_screen = getScreen()
		drawSelection()
		
		initSelectionDoneDialog()

		if len(sel) > 0:
			x = sel[0][0]
			y = sel[0][1]
			selectionMode = not selectionMode
		
		moveCursor(y, x)
		#sel.append([sel[1][0] - sel[0][0], sel[1][1] - sel[0][1]]) # width and height of selection
		#sel = []
	
def initSelectionDoneDialog():
	global h, w, selection, moveMode
	screen.addstr(h+2, 20, "m(ove)/c(opy)/d(elete)/f(flipx)/v(flipy)/r(crop)?")
	screen.refresh()
	c = screen.getch()
	if c == 109:
		# move
		toggleMoveMode(0)
	elif c == 99:
		# copy
		toggleMoveMode(1)
	elif c == 100:
		# delete
		deleteSelection()
	elif c == 102:
		# flip horizontal
		selection = flipHorizontalSelection()
		drawSelection()
		dropSelection()
	elif c == 118:
		# flip vertical
		selection = flipVerticalSelection()
		drawSelection()
		dropSelection()
	elif c == 114:
		# crop selection
		cropSelection()
	else:
		dropSelection()

	screen.addstr(h+2, 20, "                                                  ")
	screen.refresh()
	drawBorder()

def cropSelection():
	global global_screen, selection, y, x
	screen.erase()
	drawBorder()
	drawSelection()
	dropSelection()
	moveCursor(y, x)

def flipVerticalSelection():

	global selection
	miny = 9999
	maxy = -1

	for line in selection:
		if line[1] < miny:
			miny = line[1]
		if line[1] > maxy:
			maxy = line[1]

	counter = miny
	y_arr = []
	while counter <= maxy:
		y_arrie = [] 
		for line in selection:
			if line[1] == counter:
				y_arrie.append(line)
		y_arr.append(y_arrie)
		counter = counter + 1

	
	yarr = []
	counter = 0
	while counter < len(y_arr):
			
		#y_arr[counter] = newline
		newline = []
		counter1 = 0
		while counter1 < len(y_arr[counter]):
			point = []
			point.append(y_arr[counter][counter1][0])
			point.append(y_arr[counter][counter1][1])
			point.append(y_arr[len(y_arr)-counter-1][counter1][2])
			newline.append(point)
			counter1 = counter1 + 1
		
		counter = counter + 1
		yarr.append(newline)

	yarr1 = []
	for line in yarr:
		for line1 in line:
			yarr1.append(line1)

	return yarr1


def flipHorizontalSelection():

	global selection
	miny = 9999
	maxy = -1

	for line in selection:
		if line[1] < miny:
			miny = line[1]
		if line[1] > maxy:
			maxy = line[1]

	#print("min: ", miny)
	#print("max: ", maxy)

	counter = miny
	y_arr = []
	while counter <= maxy:
		y_arrie = [] 
		for line in selection:
			if line[1] == counter:
				y_arrie.append(line)
		y_arr.append(y_arrie)
		counter = counter + 1

	yarr = []

	#print("y_arr: ", y_arr)

	for line in y_arr:

		line1 = []                     # array of points of Y
		counter = 0                    # iteration of point in line
		while counter < len(line):
			
			n = len(line)-1-counter
			point = []
			point.append(line[counter][0])
			point.append(line[counter][1])
			ch = line[n][2]
			if ch == "\\":
				ch = "/"
			elif ch == "/":
				ch = "\\"
			elif ch == "[":
				ch = "]"
			elif ch == "]":
				ch = "["
			elif ch == "(":
				ch = ")"
			elif ch == ")":
				ch = "("
			elif ch == "{":
				ch = "}"
			elif ch == "}":
				ch = "{"
			elif ch == ">":
				ch = "<"
			elif ch == "<":
				ch = ">"
			elif ch == "d":
				ch = "b"
			elif ch == "b":
				ch = "d"
			point.append(ch)
			counter = counter + 1
			line1.append(point)

		yarr.append(line1)

	#print ("yarr: ", yarr)

	yarr1 = []
	for line in yarr:
		for line1 in line:
			yarr1.append(line1)

	return yarr1


def deleteSelection():
	global selection, sel, selectionMode
	printContents(getScreenWithSubtraction(global_screen, selection))
	selection = []
	sel = []
	selectionMode = False
	screen.refresh()

def getSelection():
	global y, x, selectionMode, sel
	points = [(sel[0][0], sel[0][1]), (sel[1][0], sel[1][1])]
	x_coords = [x for x in range(points[0][0], points[1][0] + 1)]
	y_coords = [y for y in range(points[0][1], points[1][1] + 1)]
	output = list(itertools.product(x_coords, y_coords))
	return output

def getSelectionWithContents(sele):
	global global_screen
	strs = global_screen
	strs_local = []
	for coord in sele:
		if strs[coord[1]][coord[0]] == " ":
			s = " "
		else:
			s = strs[coord[1]][coord[0]]
		strs_local.append([coord[0], coord[1], s])
	return strs_local

def drawSelection():
	global y, x, selectionMode, sel, selection
	for coord in selection:
		screen.addstr(coord[1], coord[0], coord[2], curses.color_pair(1))
	screen.refresh()
	#print(selection)

def getScreenWithSubtraction(strs, s):
	global selection
	new_strs = strs
	for coord in s:
		strs[coord[1]] = strs[coord[1]][:coord[0]] + " " + strs[coord[1]][coord[0]+1:]
	return new_strs

def dropSelection():
	global y, x, selectionMode, sel, selection
	selectionMode = False
	sel = []
	moveMode = -1
	strs = getScreen()
	for coord in selection:
		screen.addstr(coord[1], coord[0], strs[coord[1]][coord[0]])
	selection = []
	selectionMode = False
	screen.refresh()

def toggleMoveMode(mm):
	global moveMode
	moveMode = mm

def processSelection(y1, x1):
	global selectionMode, sel, selection, global_screen
	if selectionMode == True:
		if len(sel) >= 2:
			sel.pop()
		sel.append([x1, y1])
		#print(sel)
		selection = getSelectionWithContents(getSelection())
		printContents(global_screen)
		drawSelection()

def moveSelection(is_selected=True):
	global y, x, w, h, selection, global_screen, sel, moveMode
	
	# move
	if moveMode == 0:
		printContents(getScreenWithSubtraction(global_screen, selection))
	
	# copy
	elif moveMode == 1:
		printContents(global_screen)

	if is_selected == True:
		for coord in selection:
			if y + coord[1] - sel[0][1] and x + coord[0] - sel[0][0] >= 0 and y + coord[1] - sel[0][1] <= h and x + coord[0] - sel[0][0] <= w:
				screen.addstr(y + coord[1] - sel[0][1], x + coord[0] - sel[0][0], coord[2], curses.color_pair(1))
	else:
		for coord in selection:
			if y + coord[1] - sel[0][1] and x + coord[0] - sel[0][0] >= 0 and y + coord[1] - sel[0][1] <= h and x + coord[0] - sel[0][0] <= w:
				screen.addstr(y + coord[1] - sel[0][1], x + coord[0] - sel[0][0], coord[2])

	screen.refresh()

def animationModeOn(fnam, amode):
	global animfiles
	if amode != "marquee":
		f = open(fnam, 'r', encoding='utf-8')
		animfiles = f.readlines()
		f.close()
	else:
		animfiles = [fnam]
	animationStart(amode)

def animationStart(amode):
	global animfiles, animtime, animcount, w, h, foldername, waitingframes, marquee_h, marquee_w, cw, ch
	sx, sy = pyautogui.size()

	if amode == "file":

		counter = 0

		if os.path.isdir(foldername) == False:
			os.mkdir(foldername)
		
		first_counter = 0
		for i in range(int(animcount)):
			internal_counter = 0
			for line in animfiles:

				#if first_counter > 0:
				#	if internal_counter 25 0:
				#		internal_counter = internal_counter + 1
				#		continue

				readFile(line.replace("\n", ""))
				time.sleep(0.3)
				p = pyautogui.screenshot()
				p.save(foldername + '/p' + str(counter) + '.png')
				time.sleep(0.5)
				counter = counter + 1
				internal_counter = internal_counter + 1

			first_counter = first_counter + 1
		
		w1 = cw * (w+1)
		h1 = ch * (h+3)
		y0 = 30
		d = float(animcount)*100

		#print("counter: ", counter)

		fcounter = 0
		while fcounter < counter:
			#print("fcounter: ", fcounter)
			im = PIL.Image.open(foldername + '/p' + str(fcounter) + '.png')
			im_crop = im.crop((0, y0, w1, h1))
			im_crop.save(foldername + '/p' + str(fcounter) + '.jpg', quality=100)
			fcounter = fcounter + 1

		frames = [Image.open(image) for image in glob.glob(f"{foldername}/*.jpg")]
		frame_one = frames[0]
		frame_one.save("result.gif", format="GIF", append_images=frames,
	               save_all=True, duration=250, loop=0)

		fcounter = 0
		while fcounter < counter:
			os.remove(foldername + '/p' + str(fcounter) + '.png')
			os.remove(foldername + '/p' + str(fcounter) + '.jpg')
			fcounter = fcounter + 1

		os.rmdir(foldername)

	elif amode == "text":

		texty = 5
		startx = 10
		longestline = -1

		for line in animfiles:
			if len(line) > longestline:
				longestline = len(line)

		pngfiles = []
		if os.path.isdir(foldername) == False:
			os.mkdir(foldername)

		totalcounter = 0
		newfile = ""
		ycounter = texty
		for line in animfiles:
			line1 = line.replace("\n", "")
			counter = 0
			while counter < len(line1):
				screen.addstr(ycounter, startx+counter, line1[counter])
				screen.refresh()
				time.sleep(0.3)
				p = pyautogui.screenshot()
				if totalcounter < 10:
					fn = "0" + str(totalcounter)
				else:
					fn = str(totalcounter)
				newfile = foldername + '/' + fn + '.png'
				p.save(newfile)
				pngfiles.append(newfile)
				counter = counter + 1
				totalcounter = totalcounter + 1
				time.sleep(0.5)
				

			ycounter = ycounter + 1

		lastfile = newfile
		tc = totalcounter
		ntc = totalcounter + waitingframes

		while tc < ntc:
			if tc < 10:
				fn = "0" + str(tc)
			else:
				fn = str(tc)
			newlastfile = foldername + '/' + fn + '.png'
			shutil.copyfile(lastfile, newlastfile)
			pngfiles.append(newlastfile)
			tc = tc + 1


		w1 = cw * (longestline + 12)
		h1 = ch * (len(animfiles) + 9)
		x0 = (startx - 3) * cw
		y0 = 30 + (ch * (texty-3))
		d = float(animcount)*100

		for pngfile in pngfiles:
			im = PIL.Image.open(pngfile)
			im_crop = im.crop((x0, y0, w1, h1))
			im_crop.save(pngfile.split(".")[0] + ".jpg", quality=100)

		frames = [Image.open(image) for image in glob.glob(f"{foldername}/*.jpg")]
		frame_one = frames[0]
		frame_one.save("result.gif", format="GIF", append_images=frames,
	               save_all=True, duration=100, loop=0)

		for pngfile in pngfiles:
			os.remove(pngfile)
			os.remove(pngfile.split('.')[0] + ".jpg")

		os.rmdir(foldername)

	elif amode == "marquee":

		w = marquee_w
		h = marquee_h
		totalcounter = 0
		pngfiles = []

		if os.path.isdir(foldername) == False:
			os.mkdir(foldername)

		emptystr = ""
		for i in range(w):
			emptystr = emptystr + " "

		str1 = animfiles[0] + ""
		counter = 0
		hitleft = False
		minusx = 0
		while counter <= w + len(str1):
		
			if counter > len(str1):
				co = len(str1)
			else:
				co = counter

			str2 = str1[0:co]
			newx = w - counter
			
			if newx <= 0:

				newx = 0

				if hitleft == True:
					minusx = minusx + 1
					str2 = str2[minusx:]
				else:
					hitleft = True				

			screen.addstr(int(marquee_h/2), newx, emptystr)
			screen.addstr(int(marquee_h/2), newx, str2)
			screen.refresh()

			time.sleep(0.3)
			p = pyautogui.screenshot()
			if totalcounter < 10:
				fn = "0" + str(totalcounter)
			else:
				fn = str(totalcounter)
			p.save(foldername + '/' + fn + '.png')
			pngfiles.append(foldername + '/' + fn + '.png')
			time.sleep(0.5)

			totalcounter = totalcounter + 1
			counter = counter + 1

		w1 = cw * w
		h1 = ch * h
		x0 = 0
		y0 = 30
		d = float(animcount)*100

		for pngfile in pngfiles:
			im = PIL.Image.open(pngfile)
			im_crop = im.crop((x0, y0, w1, h1))
			im_crop.save(pngfile.split(".")[0] + ".jpg", quality=100)

		frames = [Image.open(image) for image in glob.glob(f"{foldername}/*.jpg")]
		frame_one = frames[0]
		frame_one.save("result.gif", format="GIF", append_images=frames,
	               save_all=True, duration=100, loop=0)

		for pngfile in pngfiles:
			os.remove(pngfile)
			os.remove(pngfile.split('.')[0] + ".jpg")

		os.rmdir(foldername)


def addFromFileDialog():
	global x, y

	err = False

	strs = getScreen()

	screen.erase()
	printContents(strs)
	drawBorder()
	printShiftStatus()
	printEyeDropper()

	screen.addstr(h+2, 20, "Filename:")
	editwin = curses.newwin(1, 20, h+2, 21)
	screen.refresh()
	box = Textbox(editwin)
	box.edit()
	message = box.gather()

	screen.addstr(h+2, 20, "                            ")
	screen.addstr("Paste transparent? (y/n)")
	c1 = screen.getch()

	try:

		f = open(message, 'r', encoding='utf-8')
		lines = f.readlines()
		f.close()
		counter = 0
		x0 = x
		for line in lines:
			line1 = line.replace("\n", "")
			counterx = 0
			while counterx < len(line1):
				c = line1[counterx]
				if c1 == 121:
					if c == " ":
						counterx = counterx + 1
						continue
				screen.addstr(y+counter, x+counterx, c)	
				counterx = counterx + 1
			counter = counter + 1

		strs = getScreen()

	except:

		err = True
		print("error opening file: " + message)

	screen.erase()
	printContents(strs)
	drawBorder()
	printShiftStatus()
	printEyeDropper()
	
	if err == True:
		screen.addstr(h+2, 20, "Error adding file. No file or size issues")

	screen.refresh()
	moveCursor(y, x)

def saveToImage():
	global foldername, w, h, cw, ch
	if os.path.isdir(foldername) == False:
			os.mkdir(foldername)
	p = pyautogui.screenshot()
	fn = foldername + '/temp.png'
	p.save(fn)
	im = PIL.Image.open(fn)
	x0 = 0
	y0 = 30
	w1 = cw * (w+1)
	h1 = ch * (h+3)
	im_crop = im.crop((x0, y0, w1, h1))
	im_crop.save("result.jpg", quality=100)
	os.remove(fn)
	os.rmdir(foldername)

def toggleInsertMode():
	global insertMode, y, x
	insertMode = not insertMode
	if insertMode == True:
		screen.addstr(h+2, w-30, "i")
	else:
		screen.addstr(h+2, w-30, " ")
	screen.refresh()
	moveCursor(y, x)

def printHelp():

	print("\n\n")
	print("BAKI editor v1.0")
	print("------------------------------------\n")
	print("Key controls:")
	print("ctrl + s: set size of canvas. enter comma separated width and height: 120,40")
	print("ctrl + b: shift mode switch. press space/backspace to move lines. 1 = whole line; 2 = line range till first space;")
	print("ctrl + k: erase current line")
	print("ctrl + o: move all lines up")
	print("ctrl + l: move all lines down")
	print("ctrl + u: move all lines left")
	print("ctrl + i: move all lines right")
	print("ctrl + t: move column up at cursor level")
	print("ctrl + g: move column down at cursor level")
	print("ctrl + y: toggle insert mode off/on")
	print("ctrl + p: print pattern")
	print("ctrl + x: drop eyedropper")
	print("While shiftMode=0 by pressing space you can use eyedropper symbol")
	print("print ' symbol by pressing END button\n")
	print("ctrl + r: replace characters")
	print("ctrl + q: select area/drop selection")
	print("ctrl + w: add picture from file")
	print("ctrl + d: save as jpg")
	print("To open file to edit run with filename as an argument.")
	print("\n\n\n")

def main(s):

	global x, y, w, h, symb, shiftMode, fileOpened, selectionMode, moveMode, sel, selection, insertMode
	global animfiles
	global animtime
	global animcount
	global screen

	curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

	if len(sys.argv) > 1:
		if sys.argv[1] == "-h":
			printHelp()
			return

		if sys.argv[1] == "-a":

			if len(sys.argv) > 3:
				if sys.argv[3] == "-t":
					animtime = sys.argv[4]
					if len(sys.argv) > 5:
						if sys.argv[5] == "-c":
							animcount = sys.argv[6]

			animationModeOn(sys.argv[2], "file")

		elif sys.argv[1] == "-at":

			animationModeOn(sys.argv[2], "text")

		elif sys.argv[1] == "-atm":

			animationModeOn(sys.argv[2], "marquee")

		else:
			readFile(sys.argv[1])
			toggleInsertMode()
			fileOpened = True

	if len(animfiles) < 1:

		drawBorder()
		printShiftStatus()
		printEyeDropper()
		moveCursor(y, x)
		screen.refresh()

		c = 1
		while c != 27:

			c = screen.getch()
			
			# left
			if c == 260:
				x = x - 1
				if x < 0:
					x = 0
				processSelection(y, x)
				if moveMode > -1:
					moveSelection()
				moveCursor(y, x)

			# top
			elif c == 259:
				y = y - 1
				if y < 0:
					y = 0
				processSelection(y, x)
				if moveMode > -1:
					moveSelection()
				moveCursor(y, x)

			# right
			elif c == 261:
				x = x + 1
				if x > w:
					x = w
				processSelection(y, x)
				if moveMode > -1:
					moveSelection()
				moveCursor(y, x)

			# bottom
			elif c == 258:
				y = y + 1
				if y > h:
					y = h
				processSelection(y, x)
				if moveMode > -1:
					moveSelection()
				moveCursor(y, x)

			# space: pick and draw eyedropper / shift mode
			elif c == 32:

				if shiftMode == 0:
					if symb == "":
						symb = str(curses.unctrl(screen.inch(y, x)))[2:3]
						printEyeDropper()

					drawSymbol(y, x, symb)

					if insertMode == True:
						x = x + 1
						if x > w:
							x = w
					#saveState()
					moveCursor(y, x)

				elif shiftMode == 1:

					# SHIFT MODE: MOVE --->>

					str1 = ""
					counter = x
					while counter <= w:
						c1 = screen.inch(y, counter)
						if c1 == 32:
							c1 = " "
						else:
							c1 = str(curses.unctrl(c1))[2:3]
						str1 = str1 + c1
						counter = counter + 1
					
					str1 = " " + str1.rstrip()
					
					screen.addstr(y, x, str1)
					moveCursor(y, x)
					screen.refresh()

				elif shiftMode == 2:

					# SHIFT MODE: MOVE TILL NEXT SPACE

					str1 = ""
					counter = x
					spaceFound = False
					while spaceFound == False and counter <= w:
						c1 = screen.inch(y, counter)
						if c1 == 32:
							spaceFound = True
						else:
							c1 = str(curses.unctrl(c1))[2:3]
							str1 = str1 + c1
						counter = counter + 1
						
					str1 = " " + str1
					
					screen.addstr(y, x, str1)
					moveCursor(y, x)


			# ctrl + b: shift mode
			elif c == 2:
				shiftMode = shiftMode + 1
				if shiftMode > 2:
					shiftMode = 0
				printShiftStatus()

			# ctrl + x: drop eyedropper
			elif c == 24:
				symb = ""
				printEyeDropper()

			# ctrl + x: drop eyedropper
			elif c == 11:
				deleteString(y)

			# ctrl + z: undo
			elif c == 26:
				unDo()

			# ctrl + o: move up
			elif c == 15:
				moveStringsUp()

			# ctrl + l: move down
			elif c == 12:
				moveStringsDown()

			# ctrl + p: print pattern
			elif c == 16:
				printPattern(symb, 2, True)

			# ctrl + ]: print pattern
			elif c == 0:
				printPattern(symb, 2, False)

			# ctrl + u: move everything left
			elif c == 21:
				moveStringsLeft()

			# ctrl + i: move everything right
			elif c == 9:
				moveStringsRight()

			# ctrl + s: set size
			elif c == 19:
				setCanvasSize()

			# ctrl + t: move column up
			elif c == 20:
				moveColumnUp()

			# ctrl + g: move column down
			elif c == 7:
				moveColumnDown()

			# ctrl + r: replace symbols
			elif c == 18:
				replaceSymbolDialog()

			# ctrl + n: delete column
			elif c == 14:
				deleteColumn()

			# ctrl + q: selection mode on
			elif c == 17:
				toggleSelectionMode()

			# ctrl + w: add from file
			elif c == 23:
				addFromFileDialog()

			# ctrl + d: save to image
			elif c == 4:
				saveToImage()

			# ctrl + y: insert mode off/on
			elif c == 25:
				toggleInsertMode()

			# backspace
			elif c == 8: # 127
				
				if shiftMode == 0:

					if x - 1 >= 0:
						drawSymbol(y, x-1, " ")
						#drawSymbol(y, x, " ")
						x = x - 1
						if x < 0:
							x = 0
						#saveState()
						moveCursor(y, x)

				elif shiftMode == 1:

					str1 = ""
					counter = x
					while counter <= w:
						c1 = screen.inch(y, counter)
						if c1 == 32:
							c1 = " "
						else:
							c1 = str(curses.unctrl(c1))[2:3]
						str1 = str1 + c1
						counter = counter + 1
					
					newx = x - 1
					if newx < 0:
						newx = 0
					
					screen.addstr(y, newx, str1)
					#screen.move(y, newx)
					moveCursor(y, newx)
					screen.refresh()

			# del
			elif c == 330:
				drawSymbol(y, x, " ")
				#screen.move(y, x)
				moveCursor(y, x)
				#saveState()

			# '
			elif c == 358:
				drawSymbol(y, x, "'")
				if insertMode == True:
					x = x + 1
					if x > w:
						x = w
				moveCursor(y, x)
				#saveState()

			elif c == 27:
				print("")

			else:
				drawSymbol(y, x, str(curses.unctrl(c))[2:3])
				
				if insertMode == True:
					x = x + 1
					if x > w:
						x = w

				moveCursor(y, x)

			screen.refresh()
			print(c)

		strs = getScreen()
		

		#
		#
		# SAVE TO FILE?
		#
		#

		global fname
		if fileOpened == False:
			while os.path.exists(fname) == True:
				fname = fname.split('.')[0] + "1." + fname.split('.')[1]

		screen.addstr(h+2, 20, "Save to file: " + fname + "? y(es)/c(opy)/esc")
		c = screen.getch()
		if c == 121:

			f = open(fname, "w")
			for line in strs:
				f.write(line+"\n")
			f.close()

		elif c == 99:

			f = open(fname.split('.')[0] + "1." + fname.split('.')[1], "w")
			for line in strs:
				f.write(line+"\n")
			f.close()


	curses.endwin()

curses.wrapper(main)
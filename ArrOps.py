import numpy # comes with imagesearch
from PIL import ImageGrab # DL Module Pillow/PIL [Win + Mac + Linux]
import time # built in

"""This Python module is the engine of the GemBot.
It fills amd manipulates the array of gems to calculate points and find a good move.
I have yet to try out the Max Tree RA, or the human like search for matching gem pairs in order to optimize the code."""

mode = 3 # [1] considers only the points of the initial move [2] adds points from one cascade [3] also adds points from any remaining cascades

def get_arr_TF_3Matches_1Gem(arr_AfterMove, gemVal):
	"""This function accepts a gem array and 1 gem value and returns a
	a True False array where True corresponds to 3 or more gems of the passed
	gem value in a row and/or column. The returned array can be used to count the
	number of points with the sum() function"""

	arr_TF3_1 = arr_AfterMove.copy() # preserve arr_AfterMove for getPoints
	arr0 = numpy.zeros((10,10), dtype=int)
	arr0[1:9, 1:9] = arr_TF3_1 # pad_1_zero
	arr_TF3_1 = arr0

	arr_TF3_1 = arr_TF3_1 == gemVal # Set Gem Value to True/False based on gemVal
	# print(arr_TF3_1)
	arr_TF3_Cols = arr_TF3_1.copy() # preserve original arr_TF3 to use for both Comuns and Rows
	arr_TF3_Rows = arr_TF3_1.copy() # preserve original arr_TF3 to use for both Comuns and Rows
	# print(arr_TF3_1)

	count = 0
	for r in range(10): # padded to 10 items per row and column
		for c in range(10):
			if arr_TF3_Cols[r][c] == True:
				count += 1
			else:
				if count == 1:
					arr_TF3_Cols[r][c-1] = False
				elif count == 2:
					arr_TF3_Cols[r][c-1] = False
					arr_TF3_Cols[r][c-2] = False
				count = 0
	# print(arr_TF3_Cols)
	# print(arr_TF3_Cols[1:-1, 1:-1]) # un_pad
	count = 0
	for c in range(10):
		for r in range(10):
			if arr_TF3_Rows[r][c] == True:
				count += 1
			else:
				if count == 1:
					arr_TF3_Rows[r-1][c] = False
				elif count == 2:
					arr_TF3_Rows[r-1][c] = False
					arr_TF3_Rows[r-2][c] = False
				count = 0
	# print(arr_TF3_Rows)
	# print(arr_TF3_Rows[1:-1, 1:-1]) # un_paded

	arr_TF3_1 = numpy.bitwise_or(arr_TF3_Cols, arr_TF3_Rows)
	arr_TF3_1 = arr_TF3_1[1:-1, 1:-1]
	arr_TF3_1 = arr_TF3_1.copy() # preserve for comparison in get_arr_TF_3Matches

	# print('def getPointsGem1(arr_AfterMove, gemVal):')
	# print(arr_TF3_1)
	return  arr_TF3_1 # un_paded

def get_arr_TF_3Matches(arr_AfterMove):
	"""This function accepts a gem array, loops through all gem values, and 
	returns a True False array where True corresponds to 3 or more gems in a 
	row and/or column. The returned array can be used to count the
	number of points for all gems with the sum() function"""

	# print('def getPointsGemAll(arr_AfterMove):')
	for gemVal in range(1,8):
		arr_TF3_1 = get_arr_TF_3Matches_1Gem(arr_AfterMove, gemVal)
		if gemVal == 1:
			arr_TF3_All = arr_TF3_1
		else:
			arr_TF3_All = numpy.bitwise_or(arr_TF3_All, arr_TF3_1)
	# print(arr_AfterMove)
	# print(arr_TF3_All)
	return arr_TF3_All # un padded

def get_arr_AfterCascade(arr_AfterMove, arr_TF3):
	"""This function accepts a gem array and a corresponding True False array.
	The True False array corresponds to the 3 or more gems in a row and/or column in the gem array, if any were found.
	The function returns an array of what the board would looks like after the
	matched gems disappear and the gems above fall down. This array is then further
	used to help count if any more matches could be found after."""

	arr0 = numpy.zeros((10,10), dtype=int)
	arr0[1:9, 1:9] = arr_AfterMove # pad_1_zero
	arr_AM = arr0

	arr0 = numpy.zeros((10,10), dtype=int)
	arr0 = arr0 == 1 # (all are 0 == 1 = False)
	arr0[1:9, 1:9] = arr_TF3 # pad_1_zero
	arr_TF3 = arr0

	for c in range(10):
		for r in range(10):
			if arr_TF3[r][c] == True: # https://numpy.org/devdocs/user/basics.indexing.html#assigning-values-to-indexed-arrays
				arr_AM[1:r+1, c:c+1] = arr_AM[0:r, c:c+1] # [r:r+1, c:c+1] +1 as in up to but not including
				arr_TF3[1:r+1, c:c+1] = arr_TF3[0:r, c:c+1] # [r:r+1, c:c+1] +1 as in up to but not including

	arr_AC = arr_AM[1:-1, 1:-1] # un_paded
	# print('get_arr_AfterCascade(arr_AM, arr_TF3):')
	# print(arr_AC)
	# print(arr_TF3)
	return arr_AC

def getPoints(arr_AfterMove):
	"""This function accepts a gem array of ints and calls other functions to
	calculate the total number of points that could be generated from the present arrangement.
	It counts points from both the initial move and consequent cascades, if any,
	depending on the selected mode."""

	# print('getPoints(arr_AfterMove):')
	points = 0
	arr_TF3 = get_arr_TF_3Matches(arr_AfterMove)
	points += arr_TF3.sum()

	if mode > 1:
		pointsCascade1 = 0
		arr_AC = get_arr_AfterCascade(arr_AfterMove, arr_TF3)
		arr_TF3_AC = get_arr_TF_3Matches(arr_AC)
		pointsCascade1 = arr_TF3_AC.sum()
		points += pointsCascade1

	if mode > 2:
		# print(pointsCascade1)
		while pointsCascade1 > 0:
			# print('getPoints(arr_AfterMove): while:')
			arr_AC = get_arr_AfterCascade(arr_AC, arr_TF3_AC)
			arr_TF3_AC = get_arr_TF_3Matches(arr_AC)
			pointsCascade1 = arr_TF3_AC.sum()
			points += pointsCascade1
			# print(arr_TF3_AC)

	return points#, arr_AC

def pointsMoveDown(arr_Gem, r, c):
	"""This function is 1 of 4 that changes the state of the array by moving gems in line with the function's name from the given coordinates and passing the new array for point counting."""
	arr_AfterMove = arr_Gem.copy() # preserve original arrGem for future test moves
	arr_AfterMove[r+1][c] = arr_Gem[r][c]
	arr_AfterMove[r][c] = arr_Gem[r+1][c]
	# print(arr_AfterMove)
	# return getPointsGemAll(arr_AfterMove)
	points = getPoints(arr_AfterMove)
	# if points > 0: mostPointsNextMove, *_ = getMove123(arr_AC)
	return points#, mostPointsNextMove
def pointsMoveUp(arr_Gem, r, c):
	"""This function is 1 of 4 that changes the state of the array by moving gems in line with the function's name from the given coordinates and passing the new array for point counting."""
	arr_AfterMove = arr_Gem.copy() # preserve original arrGem for future test moves
	arr_AfterMove[r-1][c] = arr_Gem[r][c]
	arr_AfterMove[r][c] = arr_Gem[r-1][c]
	# print(arr_AfterMove)
	# return getPointsGemAll(arr_AfterMove)
	points = getPoints(arr_AfterMove)
	# if points > 0: mostPointsNextMove, *_ = getMove123(arr_AC)
	return points#, mostPointsNextMove
def pointsMoveLeft(arr_Gem, r, c):
	"""This function is 1 of 4 that changes the state of the array by moving gems in line with the function's name from the given coordinates and passing the new array for point counting."""
	arr_AfterMove = arr_Gem.copy() # preserve original arrGem for future test moves'
	arr_AfterMove[r][c-1] = arr_Gem[r][c]
	arr_AfterMove[r][c] = arr_Gem[r][c-1]
	# print(arr_AfterMove)
	# return getPointsGemAll(arr_AfterMove)
	points = getPoints(arr_AfterMove)
	# if points > 0: mostPointsNextMove, *_ = getMove123(arr_AC)
	return points#, mostPointsNextMove
def pointsMoveRight(arr_Gem, r, c):
	"""This function is 1 of 4 that changes the state of the array by moving gems in line with the function's name from the given coordinates and passing the new array for point counting."""
	arr_AfterMove = arr_Gem.copy() # preserve original arrGem for future test moves
	arr_AfterMove[r][c+1] = arr_Gem[r][c]
	arr_AfterMove[r][c] = arr_Gem[r][c+1]
	# print(arr_AfterMove)
	# return getPointsGemAll(arr_AfterMove)
	points = getPoints(arr_AfterMove)
	# if points > 0: mostPointsNextMove, *_ = getMove123(arr_AC)
	return points#, mostPointsNextMove

def fill_arr_Gem(image, arr_Gem, xGemMin, yGemMin, d, gem0, arr_Gem_Str):
	"""This function fills arrGem with ints corresponding to gem colors and also fills a companion array (arrGemP) with corresponging letters for printing (for ease of reading):
	r - Red Rombus,
	g - Green Octagon,
	p - Purple Heart,
	b - Blue/Teal Cross,
	o - Orange Star,
	y - Yellow Hexagon,
	w - White/Diamond."""
	for r in range(8):
		for c in range(8):
			r1,r2,r3 = image.getpixel((xGemMin+d*c-3, yGemMin+d*r+16)) # c_at_xyRed 1 (182, 1, 1)
			g1,g2,g3 = image.getpixel((xGemMin+d*c-9, yGemMin+d*r+25)) # c_at_xyGreen 2 (0, 220, 0)
			p1,p2,p3 = image.getpixel((xGemMin+d*c-1, yGemMin+d*r+19)) # c_at_xyPurple 3 (203, 0, 203)
			b1,b2,b3 = image.getpixel((xGemMin+d*c-2, yGemMin+d*r+19)) # c_at_xyBlue 4 (0, 182, 182)
			o1,o2,o3 = image.getpixel((xGemMin+d*c-6, yGemMin+d*r+3)) # c_at_xyOrange 5 (204, 102, 0)
			y1,y2,y3 = image.getpixel((xGemMin+d*c-15, yGemMin+d*r+19)) # c_at_xyYellow 6 (255, 255, 51)
			w1,w2,w3 = image.getpixel((xGemMin+d*c-17, yGemMin+d*r+7)) # c_at_xyWhite 7 (255, 255, 255)
			if r1 >100 and r2 <10 and r3 <10: arr_Gem[r,c] = 1; arr_Gem_Str[r,c] = 'r'   # R (182, 1, 1)
			elif g1 <10 and g2 >100 and g3 <10: arr_Gem[r,c] = 2; arr_Gem_Str[r,c] = 'g' # G (0, 220, 0)
			elif p1 >100 and p2 <10 and p3 >100: arr_Gem[r,c] = 3; arr_Gem_Str[r,c] = 'p' # P (203, 0, 203)
			elif b1 <10 and b2 >100 and b3 >100: arr_Gem[r,c] = 4; arr_Gem_Str[r,c] = 'b' # B (0, 182, 182)
			elif o1 >100 and o2 >100 and o3 <10: arr_Gem[r,c] = 5; arr_Gem_Str[r,c] = 'o' # O (204, 102, 0)
			elif y1 >200 and y2 >200 and y3 <100: arr_Gem[r,c] = 6; arr_Gem_Str[r,c] = 'y' # Y (255, 255, 51)
			elif w1 >250 and w2 >250 and w3 >250: arr_Gem[r,c] = 7; arr_Gem_Str[r,c] = 'w' # W (255, 255, 255) # potential issue here if part of the board is initially covered by one of the matching pixels
			else: arr_Gem[r,c] = 0; gem0 = 1 # gem not recognized
	return gem0, arr_Gem, arr_Gem_Str

def getMove(arr_Gem):
	# [this portion could also become a function to create mode 4 which would also consider potential moves after all the initial cascades; but I'd like to look at optimization first]
	arr_Moves = get_arr_Moves(arr_Gem)
	mostPoints, mostPointsMoveName = 0, ''
	rFrom=cFrom=rTo=cTo = -1
	for r in range(8):
		for c in range(8):
			pointsDown, pointsUp, pointsLeft, pointsRight = 0, 0, 0, 0
			if arr_Moves[r][c] != 0:
				if '1' in str(arr_Moves[r][c]): pointsDown = pointsMoveDown(arr_Gem, r, c)+0.1*r # [+0.1*r] to prioritized matches lower on the board
				if '2' in str(arr_Moves[r][c]): pointsUp = pointsMoveUp(arr_Gem, r, c)+0.1*r
				if '3' in str(arr_Moves[r][c]): pointsLeft = pointsMoveLeft(arr_Gem, r, c)+0.1*r
				if '4' in str(arr_Moves[r][c]): pointsRight = pointsMoveRight(arr_Gem, r, c)+0.1*r
			if pointsDown  > mostPoints: mostPoints, mostPointsMoveName, rFrom, cFrom, rTo, cTo = pointsDown, 'Down', r, c, r+1, c
			if pointsUp > mostPoints: mostPoints, mostPointsMoveName, rFrom, cFrom, rTo, cTo = pointsUp, 'Up', r, c, r-1, c
			if pointsLeft > mostPoints: mostPoints, mostPointsMoveName, rFrom, cFrom, rTo, cTo = pointsLeft, 'Left', r, c, r, c-1
			if pointsRight > mostPoints: mostPoints, mostPointsMoveName, rFrom, cFrom, rTo, cTo = pointsRight, 'Right', r, c, r, c+1
	return mostPoints, mostPointsMoveName, rFrom, cFrom, rTo, cTo

# def get_arr_ForNextMoveAfterCascade

def get_arr_Moves(arr_Gem):
	""" This function returns an array with 0's and up to 1234 for moves: 1 Down, 2 Up, 3 Left, 4 Right.
	It is used to keep track of and reduce the # of moves to be sent for points calcualtion.
		 [[0	0	0	0		0		0		0		0]	
		  [0	0	0	0		0		0		0		0]
		  [0	0	0	0		234		204		0		0]
		  [0	0	0	1230	x		x		1204	0]
		  [0	0	0	1030	x		x		1004	0]
		  [0	0	0	0		1034	1004	0		0]
		  [0	0	0	0		0		0		0		0]
		  [0	0	0	0		0		0		0		0]] """

	arr_Moves = numpy.zeros((8,8), dtype=int)
	for r in range(8):
		for c in range(8):
			downTF = True if r < 7 else False # Test a move down if not out of bounds, but
			upTF = True if r > 0 else False # only if it hasn't already been tested at this [r][c]
			leftTF = True if c > 0 else False # (the code with long comments below is for preventing mirror moves: a Down move is the same as an Up move a row below)
			rightTF = True if c < 7 else False
			if r < 6 and arr_Gem[r+1][c] != 0 and arr_Gem[r+1][c] == arr_Gem[r+2][c]: # Twins below
				# 1 
				# 2 up
				# 3 left
				# 4 right
				# if downTF and r < 7 and '2' not in str(arr_Moves[r+1][c]) and arr_Gem[r+1][c] == arr_Gem[r+1][c]: arr_Moves[r][c] += 1000; downTF = False # [the one below] == [one above in main if] # making a move Down, have they made a move Up down there? check r below for out of bounds
				if upTF and r > 0 and '1' not in str(arr_Moves[r-1][c]) and arr_Gem[r-1][c] == arr_Gem[r+1][c]: arr_Moves[r][c] += 200; upTF = False # [the one above] == [one above in main if] # making a move Up, have they made a move Down up there? check r above for out of bounds
				if leftTF and c > 0 and '4' not in str(arr_Moves[r][c-1]) and arr_Gem[r][c-1] == arr_Gem[r+1][c]: arr_Moves[r][c] += 30; leftTF = False # [the one on the left] == [one above in main if] # making a move Left, have they made a move Right to the left of us? check c to the left for out of bounds
				if rightTF and c < 7 and '3' not in str(arr_Moves[r][c+1]) and arr_Gem[r][c+1] == arr_Gem[r+1][c]: arr_Moves[r][c] += 4; rightTF = False # [the one on the right] == [one above in main if] # making a move Right, have they made a move Left to the right of us? check c to the right for out of bounds
			if r > 1 and arr_Gem[r-1][c] != 0 and arr_Gem[r-1][c] == arr_Gem[r-2][c]: # Twins above
				# 1 down
				# 2 
				# 3 left
				# 4 right
				if downTF and r < 7 and '2' not in str(arr_Moves[r+1][c]) and arr_Gem[r+1][c] == arr_Gem[r-1][c]: arr_Moves[r][c] += 1000; downTF = False # [the one below] == [one above in main if] # making a move Down, have they made a move Up down there? check r below for out of bounds
				# if upTF and r > 0 and '1' not in str(arr_Moves[r-1][c]) and arr_Gem[r-1][c] == arr_Gem[r-1][c]: arr_Moves[r][c] += 200; upTF = False # [the one above] == [one above in main if] # making a move Up, have they made a move Down up there? check r above for out of bounds
				if leftTF and c > 0 and '4' not in str(arr_Moves[r][c-1]) and arr_Gem[r][c-1] == arr_Gem[r-1][c]: arr_Moves[r][c] += 30; leftTF = False # [the one on the left] == [one above in main if] # making a move Left, have they made a move Right to the left of us? check c to the left for out of bounds
				if rightTF and c < 7 and '3' not in str(arr_Moves[r][c+1]) and arr_Gem[r][c+1] == arr_Gem[r-1][c]: arr_Moves[r][c] += 4; rightTF = False # [the one on the right] == [one above in main if] # making a move Right, have they made a move Left to the right of us? check c to the right for out of bounds

			if c < 6 and arr_Gem[r][c+1] != 0 and arr_Gem[r][c+1] == arr_Gem[r][c+2]: # Twins to the right
				# 1 down
				# 2 up
				# 3 left
				# 4 
				if downTF and r < 7 and '2' not in str(arr_Moves[r+1][c]) and arr_Gem[r+1][c] == arr_Gem[r][c+1]: arr_Moves[r][c] += 1000; downTF = False # [the one below] == [one above in main if] # making a move Down, have they made a move Up down there? check r below for out of bounds
				if upTF and r > 0 and '1' not in str(arr_Moves[r-1][c]) and arr_Gem[r-1][c] == arr_Gem[r][c+1]: arr_Moves[r][c] += 200; upTF = False # [the one above] == [one above in main if] # making a move Up, have they made a move Down up there? check r above for out of bounds
				if leftTF and c > 0 and '4' not in str(arr_Moves[r][c-1]) and arr_Gem[r][c-1] == arr_Gem[r][c+1]: arr_Moves[r][c] += 30; leftTF = False # [the one on the left] == [one above in main if] # making a move Left, have they made a move Right to the left of us? check c to the left for out of bounds
				# if rightTF and c < 7 and '3' not in str(arr_Moves[r][c+1]) and arr_Gem[r][c+1] == arr_Gem[r][c+1]: arr_Moves[r][c] += 4; rightTF = False # [the one on the right] == [one above in main if] # making a move Right, have they made a move Left to the right of us? check c to the right for out of bounds
			if c > 1 and arr_Gem[r][c-1] != 0 and arr_Gem[r][c-1] == arr_Gem[r][c-2]: # Twins to the left
				# 1 down
				# 2 up
				# 3 
				# 4 right
				if downTF and r < 7 and '2' not in str(arr_Moves[r+1][c]) and arr_Gem[r+1][c] == arr_Gem[r][c-1]: arr_Moves[r][c] += 1000; downTF = False # [the one below] == [one above in main if] # making a move Down, have they made a move Up down there? check r below for out of bounds
				if upTF and r > 0 and '1' not in str(arr_Moves[r-1][c]) and arr_Gem[r-1][c] == arr_Gem[r][c-1]: arr_Moves[r][c] += 200; upTF = False # [the one above] == [one above in main if] # making a move Up, have they made a move Down up there? check r above for out of bounds
				# if leftTF and c > 0 and '4' not in str(arr_Moves[r][c-1]) and arr_Gem[r][c-1] == arr_Gem[r][c-1]: arr_Moves[r][c] += 30; leftTF = False # [the one on the left] == [one above in main if] # making a move Left, have they made a move Right to the left of us? check c to the left for out of bounds
				if rightTF and c < 7 and '3' not in str(arr_Moves[r][c+1]) and arr_Gem[r][c+1] == arr_Gem[r][c-1]: arr_Moves[r][c] += 4; rightTF = False # [the one on the right] == [one above in main if] # making a move Right, have they made a move Left to the right of us? check c to the right for out of bounds

			if 0 < r < 7 and arr_Gem[r-1][c] != 0 and arr_Gem[r-1][c] == arr_Gem[r+1][c]: # One story apart
				# 1 
				# 2 
				# 3 left
				# 4 right
				# if downTF and r < 7 and '2' not in str(arr_Moves[r+1][c]) and arr_Gem[r+1][c] == arr_Gem[r-1][c]: arr_Moves[r][c] += 1000; downTF = False # [the one below] == [one above in main if] # making a move Down, have they made a move Up down there? check r below for out of bounds
				# if upTF and r > 0 and '1' not in str(arr_Moves[r-1][c]) and arr_Gem[r-1][c] == arr_Gem[r-1][c]: arr_Moves[r][c] += 200; upTF = False # [the one above] == [one above in main if] # making a move Up, have they made a move Down up there? check r above for out of bounds
				if leftTF and c > 0 and '4' not in str(arr_Moves[r][c-1]) and arr_Gem[r][c-1] == arr_Gem[r-1][c]: arr_Moves[r][c] += 30; leftTF = False # [the one on the left] == [one above in main if] # making a move Left, have they made a move Right to the left of us? check c to the left for out of bounds
				if rightTF and c < 7 and '3' not in str(arr_Moves[r][c+1]) and arr_Gem[r][c+1] == arr_Gem[r-1][c]: arr_Moves[r][c] += 4; rightTF = False # [the one on the right] == [one above in main if] # making a move Right, have they made a move Left to the right of us? check c to the right for out of bounds
			if 0 < c < 7 and arr_Gem[r][c-1] != 0 and arr_Gem[r][c-1] == arr_Gem[r][c+1]: # One door apart
				# 1 down
				# 2 up
				# 3
				# 4
				if downTF and r < 7 and '2' not in str(arr_Moves[r+1][c]) and arr_Gem[r+1][c] == arr_Gem[r][c-1]: arr_Moves[r][c] += 1000; downTF = False # [the one below] == [one above in main if] # making a move Down, have they made a move Up down there? check r below for out of bounds
				if upTF and r > 0 and '1' not in str(arr_Moves[r-1][c]) and arr_Gem[r-1][c] == arr_Gem[r][c-1]: arr_Moves[r][c] += 200; upTF = False # [the one above] == [one above in main if] # making a move Up, have they made a move Down up there? check r above for out of bounds
				# if leftTF and c > 0 and '4' not in str(arr_Moves[r][c-1]) and arr_Gem[r][c-1] == arr_Gem[r][c-1]: arr_Moves[r][c] += 30; leftTF = False # [the one on the left] == [one above in main if] # making a move Left, have they made a move Right to the left of us? check c to the left for out of bounds
				# if rightTF and c < 7 and '3' not in str(arr_Moves[r][c+1]) and arr_Gem[r][c+1] == arr_Gem[r][c-1]: arr_Moves[r][c] += 4; rightTF = False # [the one on the right] == [one above in main if] # making a move Right, have they made a move Left to the right of us? check c to the right for out of bounds
	# print(arr_Moves)
	return arr_Moves

# def stymie(levelMax, levelCur, mostPoints, xGemMin, yGemMin, run_program):
# 	""" This function attemts to stymie the bot from going to levels with yet unsustainable timers.
# 	By slowing down at a sustainable level a higher score is reachable in the long run.
# 	Ideally, bot needs to be made more efficient so this can happen naturally or at higher levels with fewer pauses. """
# 	# levelMax = 22 is the current set up
# 	if level > levelMax:
# 		print(f'Exiting because current level {level} > {levelMax} levelMax. This is due to HighScore attempt. Comment out conditions at the bottom or change levelMax: stymie(mostPoints, levelCur, levelMax).')
# 		on_press(Key.space) # pause
# 	if level >= levelMax:
# 		# lvl 20 .60 2s 1s [2.5 mil 4hrs]
# 		timerDelay = .70 # % of timer bar
# 		image = ImageGrab.grab()
# 		red, *_ = image.getpixel((xGemMin-30+(45*8)*timerDelay, yGemMin-25)) # % of timer bar
# 		while red >= 10 and run_program: # let the timer run to stay on level
# 			image = ImageGrab.grab()
# 			red, *_ = image.getpixel((xGemMin-30+(45*8)*timerDelay, yGemMin-25)) # % of timer bar
# 			if mostPoints > 10: print(f'timer check, {1.5} second break'); time.sleep(2)
# 			elif mostPoints > 5: print(f'timer check, {.5} second break'); time.sleep(1)
# 			else: print(f'timer check, go go go'); red = 0 # 7 sec for 45% to deplete

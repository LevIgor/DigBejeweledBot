from pynput.mouse import Button, Controller # DL Module pynput [Win + Mac]
mouse = Controller()
from pynput.keyboard import Key, Controller # DL Module pynput [Win + Mac]
keyboard = Controller()
from pynput import keyboard # # DL Module pynput [Win + Mac]
from PIL import ImageGrab # DL Module Pillow/PIL [Win + Mac + Linux]
from python_imagesearch.imagesearch import imagesearch # DL Module imagesearch [Win + Mac + Linux]
import numpy # comes with imagesearch [or Pillow]
import time # built in
import sys # built in
import argparse # built in
import ArrOps # custom

"""This Python module is the body of the GemBot.
It calls on the engine and adds a few conveniences.
For example, it recognizes when (but not which) any key is pressed in order to stop the bot,
it finds the board, facilitates the moves, and tracks the levels."""

parser = argparse.ArgumentParser(description='This program accepts one optional argument via the command line. \
	The usage is: python GemBot.py -m [or --mode] int_value.\
	The int_value can be either 1, 2, or 3 and corresponds to the following: \
	[1] consider only the initial points of each move [2] add points from one cascade [3] also add points from any remaining cascades. \
	The default mode is 3')
parser.add_argument('-m', '--mode', type=int, choices={1, 2, 3}, default=3)
args = parser.parse_args()
ArrOps.mode = args.mode
if len(sys.argv) > 1: # a bit overboard but just wanted to see what happens
	if args.mode == 1: print('args accepted, mode set to 1')
	elif args.mode == 2: print('args accepted, mode set to 2')
	elif args.mode == 3: print('args accepted, mode set to 3')
else: print('no args passed, default mode = 3')

# to exit - press any key

run_program = True
def on_press(key):
	"""This function waits for key strokes. If it detects any key press, the game is paused inside the browser and the bot is stopped via sys.exit() or via run_program = False until it runs through any remaining loops."""
	# print (key)
	# if key == keyboard.Key.space or key == keyboard.Key.esc or key == keyboard.Key.pause or key == keyboard.Key.ctrl_l: # CTRL key on the Left side of the keyboard
	global run_program; run_program = False
	mouse.position = (xPause, yPause); time.sleep(.01)
	mouse.press(Button.left); mouse.release(Button.left)
	with open('./levelcount.txt', 'w') as lvlfile:
		lvlfile.write(str(level))
	print('Bot exiting')
	sys.exit()
print ('to exit - press any key')

# Find game board, set coordinates

pos = imagesearch('./anchor.png') # 586[+183] 194[+15] [+ to the top left gem's pixel]
if pos[0] != -1: print('anchor.png found, position : ', pos[0], pos[1]); xAnchor, yAnchor = pos[0], pos[1]
else: print("can't see game"); sys.exit()
mouse.position = (xAnchor, yAnchor); time.sleep(0.01); mouse.press(Button.left); mouse.release(Button.left) # Bring into view in case obscured
xGemMin, yGemMin = xAnchor+183, yAnchor+10 # top left gem [anchor.png x,y + offset]
d = 45 # Distance between gems in pixels
xPause, yPause = xAnchor+62, yAnchor+283 # Options menu on exit to pause game play
xLvlup, yLvlup = xAnchor+337, yAnchor+160 # (255,255,255)
xGameOver, yGameOver = xAnchor+199, yAnchor+20 # (255,255,255)

# Check for restart and level count (data persistence)

pos = imagesearch('./lvl1.png')
if pos[0] != -1:
	level = 1;	print('lvl1.png found, position : ', pos[0], pos[1], 'level =', level)
	pos = imagesearch('./resume.png')
	if pos[0] != -1: mouse.position = (pos[0]+250, pos[1]+20); time.sleep(0.01); mouse.press(Button.left); mouse.release(Button.left) # Resume (hit Ok in the Options menu)
else:
	print('lvl1.png not found (some other level), checking if pause (Options menu) is open...')
	pos = imagesearch('./resume.png')
	if pos[0] != -1:
		print('resume.png (pause menu) found, position : ', pos[0], pos[1], 'retreiving saved level count from levelcount.txt')
		lvlfile = None
		try:
			with open('./levelcount.txt', 'r') as lvlfile:
				level = int(next(lvlfile)) # starting/current level from a txt file to use at bot restart, a check is also be performed just above for starting at level 1.
				print('Retreived level count from levelcount.txt, level =', level)
		except FileNotFoundError:
			print('levelcount.txt not found, board not at level 1, not sure what the level it is, setting level to -240'); level = -240
		except StopIteration:
			print('levelcount.txt found but empty, board not at level 1, not sure what the level it is, setting level to -240'); level = -240
		except ValueError:
			print('levelcount.txt found but appears corrupt, board not at level 1, not sure what the level it is, setting level to -240'); level = -240
		except:
			print('An error occured while trying to read from levelcount.txt, board not at level 1, not sure what the level it is, setting level to -240'); level = -240
		else:
			lvlfile.close()
		mouse.position = (pos[0]+250, pos[1]+20); time.sleep(0.01); mouse.press(Button.left); mouse.release(Button.left) # Resume (hit Ok in the Options menu)
	else: print('resume.png (pause menu) not found, not level 1, not sure what the level is [if lavel has not changed, exit and restart bot so it reads from levelcount.txt], setting level to -240 for now'); level = -240

# main loop

arr_Gem = numpy.zeros((8,8), dtype=int)
arr_Gem_Str = numpy.zeros((8,8), dtype=str)
with keyboard.Listener(on_press=on_press) as listener:
	while run_program:
		mouse.position = (xAnchor, yAnchor) # moving the cursor off gems prevents mouseover color change, results in faster array refill, because extra color checks are't necessary'
		gem0 = 1
		while gem0 and run_program:
			gem0 = 0
			image = ImageGrab.grab()
			if image.getpixel((xLvlup, yLvlup)) == (255,255,255):
				print('level up!')
				while image.getpixel((xLvlup, yLvlup)) == (255,255,255):
					image = ImageGrab.grab() # wait for level up screen
				level += 1; print('next level =', level)
			if image.getpixel((xGameOver, yGameOver)) == (255,255,255): print('Game Over, timer ran out, level =', level); run_program = False; sys.exit()
# fill arr_Gem
			gem0, arr_Gem, arr_Gem_Str = ArrOps.fill_arr_Gem(image, arr_Gem, xGemMin, yGemMin, d, gem0, arr_Gem_Str)
			# print(arr_Gem)
		# print(arr_Gem)
# get move
		mostPoints, mostPointsMoveName, rFrom, cFrom, rTo, cTo = ArrOps.getMove(arr_Gem)
# make move
		if mostPoints > 0 and run_program:
			print(f'mode = {ArrOps.mode}, level = {level}, [r{rFrom+1}, c{cFrom+1}] move [{mostPointsMoveName}] for mostPoints [{mostPoints}]:')
			print(numpy.array2string(arr_Gem_Str, formatter={'str_kind':lambda x: x}))
			mouse.position = (xGemMin+cFrom*d, yGemMin+rFrom*d); time.sleep(.01)#; stymie(levelMax, levelCur, mostPoints, xGemMin, yGemMin, run_program)
			mouse.press(Button.left); mouse.release(Button.left)
			mouse.position = (xGemMin+cTo*d, yGemMin+rTo*d); time.sleep(.01) # sleep time here can be adjusted depending on system
			mouse.press(Button.left); mouse.release(Button.left)
		elif run_program == False: print('Bot finishing up last loop')
		else: print('Out of moves')
	listener.join()
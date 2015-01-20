# -*- coding: utf-8 -*-
import sys, pygame
from pygame.locals import *
import time
import subprocess
import os
import glob
import re
import pylast
from mpd import MPDClient
from math import ceil
import datetime
from datetime import timedelta
import pitft_ui
from signal import alarm, signal, SIGALRM, SIGKILL

# Setting up MPD Clinet
client = MPDClient()
client.timeout = 10
client.idletimeout = None
noConnection = True
while noConnection:
	try:
		client.connect("localhost", 6600)
		noConnection=False
	except Exception, e:
		print e
		noConnection=True
		time.sleep(15)

# OS enviroment variables for pitft
os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
os.environ["SDL_MOUSEDRV"] = "TSLIB"

# Init pygame
pygame.init()
pygame.mouse.set_visible(False)

##### PYLAST ##################################################################
# You have to have your own unique two values for API_KEY and API_SECRET
# Obtain yours from http://www.last.fm/api/account for Last.fm
API_KEY = "dcbf56084b47ffbd3cc6755724cb12fa"
API_SECRET = "a970660ef47453134192fa6a9fa6da31"

# In order to perform a write operation you need to authenticate yourself
#username = "your_user_name"
#password_hash = pylast.md5("your_password")
network = pylast.LastFMNetwork(api_key = API_KEY, api_secret = API_SECRET)

##### SCREEN MANAGER ##########################################################
sm = pitft_ui.PmbPitft(client, network)

#define function that checks for mouse location
def on_click():
	click_pos = (pygame.mouse.get_pos() [0], pygame.mouse.get_pos() [1])

	if sm.get_backlight_status() == 0 and 0 <= click_pos[0] <= 320 and 0 <= click_pos[1] <= 240:
		print "Screen off, Screen touch"
		button(9) 

	if 223 <= click_pos[0] <= 285 and 6 <= click_pos[1] <=31:
		print "Toggle repeat" 
		button(0)
	if 223 <= click_pos[0] <= 285 and 38 <= click_pos[1] <=63:
		print "Toggle random"
		button(1)	

	# Volume
        if 188 <= click_pos[0] <= 226 and 65 <= click_pos[1] <=100:
                print "Volume-"
                button(2)
        if 281 <= click_pos[0] <= 319 and 65 <= click_pos[1] <=100:
                print "Volume+"
                button(3)

	# SLEEP
        if 188 <= click_pos[0] <= 226 and 103 <= click_pos[1] <=138:
                print "Sleep-"
                button(4)
        if 281 <= click_pos[0] <= 319 and 103 <= click_pos[1] <=138:
                print "Sleep+"
                button(5)

	# Controls
        if 194 <= click_pos[0] <= 232 and 144 <= click_pos[1] <=182:
                print "Prev"
                button(6)
        if 234 <= click_pos[0] <= 272 and 144 <= click_pos[1] <=182:
                print "Toggle play/pause"
                button(7)
        if 273 <= click_pos[0] <= 311 and 144 <= click_pos[1] <=182:
                print "Next"
                button(8)

	# Screen off
        if 280 <= click_pos[0] <= 320 and 200 <= click_pos[1] <=240:
                print "Screen off"
                button(9)


#define action on pressing buttons
def button(number):
	print "You pressed button ",number
	if number == 0:    #specific script when exiting
		sm.toggle_repeat()

	if number == 1:	
		sm.toggle_random()

	if number == 2:
		sm.set_volume(1, "-")

	if number == 3:
		sm.set_volume(1, "+")
		
	if number == 4:
		sm.adjust_sleeptimer(15, "-")

	if number == 5:
		sm.adjust_sleeptimer(15, "+")

	if number == 6:
		sm.control_player("previous")

	if number == 7:
		sm.toggle_playback()

	if number == 8:
		sm.control_player("next")

	if number == 9:
		sm.toggle_backlight()
	
def main():
	drawtime = datetime.datetime.now()
	while 1:
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN:
				print "screen pressed" #for debugging purposes
				pos = (pygame.mouse.get_pos() [0], pygame.mouse.get_pos() [1])
				print pos #for checking
				#pygame.draw.circle(screen, (255,255,255), pos, 2, 0) #for debugging purposes - adds a small dot where the screen is pressed
				on_click()

			#ensure there is always a safe way to end the program if the touch screen fails
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					print "ESCAPE"
					
					# Close MPD connection
					client.close()
					client.disconnect()
					sys.exit()

		# Update screen
		if drawtime < datetime.datetime.now():
			drawtime = datetime.datetime.now() + timedelta(milliseconds=500)
			sm.refresh_mpd()
			sm.parse_mpd()
			sm.render(screen)
			pygame.display.flip()
	pygame.display.update()

#################### EVERTHING HAS NOW BEEN DEFINED ###########################

#set size of the screen
size = width, height = 320, 240
screen = pygame.display.set_mode(size)

## HAX FOR FREEZING ##
class Alarm(Exception):
	pass
def alarm_handler(signum, frame):
	raise Alarm
signal(SIGALRM, alarm_handler)
alarm(3)
try:
	# Set screen size
	size = width, height = 320, 240
	screen = pygame.display.set_mode(size)
	alarm(0)
except Alarm:
	raise KeyboardInterrupt
## HAX END ##


print pygame.display.get_driver()

main() #check for key presses and start emergency exit

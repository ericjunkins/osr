import os
import socket
import glob
import time
import RPi.GPIO as GPIO
from bluetooth import *
from controls import Rover
import threading
import math
import select
import sys
from arguments import Arguments
from connections import Connections


args = Arguments()
conn = Connections()
rover = Rover()

def listener():
	if args.results.socket == True:
		print "starting LED socket client"
	if args.results.test == True:
		print "starting test mode"
	elif args.results.connection == 'x' or args.results.connection == 'b':
		conn.connect(args.results.connection)

def main():
	listener()
	while True:
		try:
			v,r = conn.getDriveVals()
			#encs =[0]*4
			rover.spinCorner(rover.calculateCornerAngles(r))
			rover.drive(rover.calculateDriveSpeed(v,rover.getTurningRadius(rover.getScaledEnc())))
			time.sleep(0.05)

		except KeyboardInterrupt:
			rover.killMotors()
			conn.closeConnections()
			time.sleep(0.5)
			listener()

if __name__ == '__main__':
	main()




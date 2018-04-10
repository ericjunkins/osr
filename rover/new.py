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


def main():
	args = Arguments()
	conn = Connections()
	rover = Rover()
	if args.results.socket == True:
		print "starting LED socket client"

	if args.results.test == True:
		print "starting test mode"
	elif args.results.connection == 'x' or args.results.connection == 'b':
		conn.connect(args.results.connection)

	while True:
		try:
			v,r = conn.getDriveVals()
			encs = rover.getScaledEnc()
			print encs
			encs =[0]*4
			cur_rad = rover.getTurningRadius(encs)
			rover.drive(rover.calculateDriveSpeed(v,rover.getTurningRadius(encs)))

			time.sleep(0.05)

		except KeyboardInterrupt:
			conn.closeConnections()



if __name__ == '__main__':
	main()




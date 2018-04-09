import os
import socket
import glob
import time
import RPi.GPIO as GPIO
from bluetooth import *
import controls as rover
import threading
import math
import select
import sys
from arguments import Arguments
from connections import Connections


def main():
	args = Arguments()
	conn = Connections()
	if args.results.socket == True:
		print "starting LED socket client"

	if args.results.test == True:
		print "starting test mode"
	elif args.results.connection == 'x' or args.results.connection == 'b':
		conn.connect(args.results.connection)

if __name__ == '__main__':
	main()




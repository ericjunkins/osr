import time
from controls import Rover
from arguments import Arguments
from connections import Connections

args = Arguments()
conn = Connections()
rover = Rover()

def listener():
	if args.socket == True:
		print "starting LED socket client"
		conn.unixSockConnect()

	if args.test == True:
		print "starting test mode"
	elif args.connect == 'x' or args.connect == 'b':
		conn.connect(args.connect)
	else:
		conn.connect('b')

def main():
	listener()
	while True:
		try:
			v,r = conn.getDriveVals()
			rover.drive(v,r)
		except:
			rover.killMotors()
			conn.closeConnections()
			time.sleep(0.5)
			listener()

if __name__ == '__main__':
	main()




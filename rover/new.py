import time
from controls import Rover
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
	else:
		conn.connect('b')

def main():
	listener()
	while True:
		try:
			rover.drive(conn.getDriveVals())
		except:
			rover.killMotors()
			conn.closeConnections()
			time.sleep(0.5)
			listener()

if __name__ == '__main__':
	main()




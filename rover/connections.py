import socket
import os
import time
import xbox
from bluetooth import *



class Connections():

	def __init__(self):
		self.type = "b"
		self.joy = None
		self.bt_sock = None
		self.check = 0

	def btConnect(self):
		server_sock = BluetoothSocket(RFCOMM)
		server_sock.bind(("",PORT_ANY))
		server_sock.listen(1)

		port = server_sock.getsockname()[1]
		uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

		advertise_service( server_sock, "raspberrypi",
						   service_id = uuid,
						   service_classes = [uuid, SERIAL_PORT_CLASS],
						   profiles = [SERIAL_PORT_PROFILE],
						   )
		print "waiting for connection on RFCOMM channel %d" % port
		client_socket, client_info = server_sock.accept()
		client_socket.setblocking(0)
		print "Accepted connection from ", client_info
		self.bt_sock = client_socket
		self.bt_sock.settimeout(1)

	def xBoxConnect(self):
		self.joy = xbox.Joystick()
		print 'starting xbox list'


	def connect(self,type):
		if type == "b":
			self.btConnect()
		elif type == "x":
			self.xBoxConnect()
		else:
			return -1
		self.type = type

	def _btVals(self):
		try:
			sockData = self.bt_sock.recv(1024)
			v,s,c = ord(sockData[3]),ord(sockData[7]),ord(sockData[-1])

			if (v ^ s is c):
				#self.drive_speed = v-100
				#self.turn_radius = s-100
				return (v-100,s-100)
				#self.screen = ord(sockData[11])
			else:
				print "Checksum failed!"
				self.check +=1
				if check > 3:
					self.bt_sock.close()
			self.bt_sock.send("1")
		except:
			print "exiting"
			self.bt_sock.send("0")
			time.sleep(0.25)
			self.bt_sock.close()
			return (0,0)


	def closeConnections(self):
		if self.type == 'b':
			self.bt_sock.send('0')
			time.sleep(0.25)
			self.bt_sock.close()
		elif self.typ == 'x':
			self.joy.close()

	def _xboxVals(self):
		if joy.connected():
			return (joy.leftY(),joy.rightX())

	def getDriveVals(self):
		if self.type == 'b':
			v,r = self._btVals()
		elif self.type == 'x':
			v,r = self._xboxVals()
		return v,r


	

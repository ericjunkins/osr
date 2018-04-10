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
			self.bt_sock.send('1')
			return (v-100,s-100)
		except KeyboardInterrupt:
			print "exiting btvals"


	def closeConnections(self):
		if self.type == 'b':
			try:
				self.bt_sock.send('0')
				time.sleep(0.25)
				self.bt_sock.close()
			except:
				pass		
		elif self.type == 'x':
			self.joy.close()

	def _xboxVals(self):
		if self.joy.connected():
			return (int(self.joy.leftY()*100),int(self.joy.rightX()*100))
		else:
			print 'not connected from xbox controller'
			return (0,0)

	def getDriveVals(self):
		if self.type == 'b':
			v,r = self._btVals()
		elif self.type == 'x':
			v,r = self._xboxVals()
		return v,r



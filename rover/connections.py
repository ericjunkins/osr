import socket
import os
import time





class Connections():
	
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
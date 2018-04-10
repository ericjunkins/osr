import argparse

class Arguments():
	def __init__(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('-t', action='store_true', dest = 'test',
							default = False,
							help='Turn on testing mode',
							)
		parser.add_argument('-s', action='store_true', dest = 'socket',
							default = False,
							help='Turn on LED socket',
							)
		parser.add_argument('-c', action='store', dest = 'connection',
							default = False,
							help='Turn on bluetooth listener',
							)
		
		self.connect = parser.parse_args().connection
		self.socket = parser.parse_args().socket
		self.test = parser.parse_args().test

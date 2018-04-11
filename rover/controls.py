#!/usr/bin/env python
import time
import serial
import math
from roboclaw import Roboclaw
import config



d1,d2,d3,d4 = config.d1,config.d2,config.d3,config.d4  #Physical distances on Rover
cals = config.cals                                     #Calibration constants



class Rover():
	'''
	Rover class contains all the math and motor control algorithms to move the rover

	In order to call command the rover the only method necessary is the drive() method

	'''
	def __init__(self):
		'''
		Initialization of communication parameters for the Motor Controllers
		'''

		self.rc = Roboclaw("/dev/ttyS0",115200)
		self.rc.Open()
		self.address = [0x80,0x81,0x82,0x83,0x84]
		self.rc.ResetEncoders(self.address[0])
		self.rc.ResetEncoders(self.address[1])
		self.rc.ResetEncoders(self.address[2])


	def getScaledEnc(self):
		'''
		Returns a list of angles [Deg] that each of the Corners are currently pointed at
		'''

		encoders = [0]*4
		for i in range(4):
			index = int(math.ceil((i+1)/2.0)+2)
			if (i % 2):
				enc = self.rc.ReadEncM2(self.address[index])[1]
			else:
				enc = self.rc.ReadEncM1(self.address[index])[1]
			encoders[i] = int(cals[i][0] * math.pow(enc,2) + cals[i][1]*enc + cals[i][2])
		return encoders

	@staticmethod
	def getTurningRadius(enc):
		'''
		Takes the list of current corner angles and approximates the current turning radius [inches]

		:param list [int] enc: List of encoder ticks for each corner motor

		'''
		if enc[0] == None:
			return 250
		try:
			if enc[0] > 0:
				r1 = (d1/math.tan(math.radians(abs(enc[0])))) + d3
				r2 = (d2/math.tan(math.radians(abs(enc[1])))) + d3
				r3 = (d2/math.tan(math.radians(abs(enc[2])))) - d3
				r4 = (d1/math.tan(math.radians(abs(enc[3])))) - d3
			else:
				r1 = -(d1/math.tan(math.radians(abs(enc[0])))) - d3
				r2 = -(d2/math.tan(math.radians(abs(enc[1])))) - d3
				r3 = -(d2/math.tan(math.radians(abs(enc[2])))) + d3
				r4 = -(d1/math.tan(math.radians(abs(enc[3])))) + d3
			radius = (r1 + r2 + r3 + r4)/4
			return radius
		except:
			return 250

	@staticmethod
	def getTarAng(radius):
		'''
		Takes a turning radius and calculates what angle [degrees] each corner should be at

		:param int radius: Radius drive command, ranges from -100 (turning left) to 100 (turning right)

		'''

		#Scaled from 250 to 220 inches. For more information on these numbers look at the Software Controls.pdf
		if radius == 0:
			r = 250
		elif -100 <= radius <= 100:
			r = 250 - radius*(220/100)
		else:
			r = 250

		if (radius > 0):
			ang1 = -int(math.degrees(math.atan(d1/(abs(r)+d3))))
			ang2 =  int(math.degrees(math.atan(d2/(abs(r)+d3))))
			ang3 =  int(math.degrees(math.atan(d2/(abs(r)-d3))))
			ang4 = -int(math.degrees(math.atan(d1/(abs(r)-d3))))
		elif (radius < 0):
			ang1 =  int(math.degrees(math.atan(d1/(abs(r)-d3))))
			ang2 = -int(math.degrees(math.atan(d2/(abs(r)-d3))))
			ang3 = -int(math.degrees(math.atan(d2/(abs(r)+d3))))
			ang4 =  int(math.degrees(math.atan(d1/(abs(r)+d3))))
		else:
			ang1,ang2,ang3,ang4 = 0,0,0,0

		return [ang2,ang1,ang4,ang3]

	@staticmethod
	def getVelocity(v,r):
		'''
		Returns a list of speeds for each individual drive motor based on current turning radius

		:param int v: Drive speed command range from -100 to 100
		:param int r: Turning radius command range from -100 to 100

		'''

		v = int(v)*(127/100)
		if (v == 0):
			return [v]*6

		if (r == 0 or r >= 250 or r <= -250):
				return [v] * 6                        # No turning radius, all wheels same speed
		else:
			x = speed/(abs(r) + d4)                   # Wheels can't move faster than max (127)
			a = math.pow(d2,2)
			b = math.pow(d3,2)
			c = math.pow(abs(r) + d1,2)
			d = math.pow(abs(r) - d1,2)
			e = abs(r) - d4


			v1 = int(x*math.sqrt(b + d))
			v2 = int(x*e)                             # Slowest wheel
			v3 = int(x*math.sqrt(a + d))
			v4 = int(x*math.sqrt(a + c))
			v5 = int(speed)                           # Fastest wheel
			v6 = int(x*math.sqrt(b + c))

			if (r < 0):
				velocity = [v1,v2,v3,v4,v5,v6]
			elif (r > 0):
				velocity = [v6,v5,v4,v3,v2,v1]
			return velocity

	def spinCorner(self, tar_enc):
		'''
		Takes the target angle and gets what encoder tick that value is for position control

		:param list [int] tar_enc: List of target angles in degrees for each corner
		'''
		x = [0]*4
		for i in range(4):
			a, b, c = cals[i][0], cals[i][1], cals[i][2] - tar_enc[i]
			d = b**2-4*a*c
			if d < 0:
				print 'no soln'
			elif d == 0:
				x[i] = int((-b + math.sqrt(d[i])) / (2 * a))
			else:
				x1 = (-b + math.sqrt(d)) / (2 * a)
				x2 = (-b - math.sqrt(d)) / (2 * a)
				if x1 > 0 and x2 <=0:
					x[i] = int(x1)
				else:
					x[i] = int(x2)          #I don't think this case can ever happen.

		speed, accel = 1000,2000            #These values could potentially need tuning still


		for i in range(4):
			index = int(math.ceil((i+1)/2.0)+2)
                        if (i % 2):
				self.rc.SpeedAccelDeccelPositionM2(self.address[index],accel,speed,accel,x[i],1)
                        else:
				self.rc.SpeedAccelDeccelPositionM1(self.address[index],accel,speed,accel,x[i],1)


	def spinMotor(self, motorID, speed):
		'''
		Wrapper method for an easier interface to control the motors

		:param int motorID: number that corresponds to each physical motor
		:param int speed: Speed for each motor, range from 0-127

		'''
		addr = {0: self.address[3],
				1: self.address[3],
				2: self.address[4],
				3: self.address[4],
				4: self.address[0],
				5: self.address[0],
				6: self.address[1],
				7: self.address[1],
				8: self.address[2],
				9: self.address[2]}

		#drive forward
		if (speed >= 0):
			command = {0: self.rc.ForwardM1,
					   1: self.rc.ForwardM2,
					   2: self.rc.ForwardM1,
					   3: self.rc.ForwardM2,
					   4: self.rc.ForwardM1,
					   5: self.rc.BackwardM2, #some are backward based on wiring diagram
					   6: self.rc.ForwardM1,
					   7: self.rc.ForwardM2,
					   8: self.rc.BackwardM1,
					   9: self.rc.ForwardM2}
		#drive backward
		else:
			command = {0: self.rc.BackwardM1,
					   1: self.rc.BackwardM2,
					   2: self.rc.BackwardM1,
					   3: self.rc.BackwardM2,
					   4: self.rc.BackwardM1,
					   5: self.rc.ForwardM2,
					   6: self.rc.BackwardM1,
					   7: self.rc.BackwardM2,
					   8: self.rc.ForwardM1,
					   9: self.rc.BackwardM2}

		speed = abs(speed)
		return command[motorID](addr[motorID],speed)



	def drive(self,v,r):
		'''
		Driving method for the Rover

		:param int v: driving velocity command, % based from -100 (backward) to 100 (forward)
		:param int r: driving turning radius command, % based from -100 (left) to 100 (right)

		'''
		current_radius = self.getTurningRadius(self.getScaledEnc())
		velocity = self.getVelocity(v, current_radius)
		self.spinCorner(self.getTarAng(r))
		for i in range(6):
			self.spinMotor(i+4,velocity[i])


	def killMotors(self):
		'''
		Stops all motors on Rover
		'''
		for i in range(0,10):
			self.spinMotor(i,0)

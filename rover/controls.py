#!/usr/bin/env python
import time
import serial
import math
from roboclaw import Roboclaw
import threading
import config

d1 = config.d1
d2 = config.d2
d3 = config.d3
d4 = config.d4

cals = config.cals

class Rover():
	def __init__(self):
		self.encoders = [None]*4
		self.thread_kill = False
		self.turning_radius = 250
		self.is_data = False
		self.__motor_speeds = [0]*10
		self.__tar_deg = [0]*4
		self.__linear_speed = 0
		self.rc = Roboclaw("/dev/ttyS0",115200)
		self.rc.Open()
		self.address = [0x80,0x81,0x82,0x83,0x84]

		self.rc.ResetEncoders(self.address[0])
		self.rc.ResetEncoders(self.address[1])
		self.rc.ResetEncoders(self.address[2])

	#Sends speed of drive motors based on input and current turning radius
	def calculateDriveSpeed(self,v,cur_rad):
		v = int(v)*(127/100)
		if (v == 0):
			return [0]*6
		else:
			return  self.__getVelocity(cur_rad,v)


	#Gets the current approximate turning radius of the rover based on current corner angles
	def getTurningRadius(self,enc):
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

	#Calculates the angles the corners need to be at given an input desired turning radius r
	def calculateCornerAngles(self,r):
		tmp_radius = r
		if tmp_radius > 0:
			r = 220 - tmp_radius*(250/100)
		elif tmp_radius < 0:
			r = -220 - tmp_radius * (250/100)
		else:
			r = 250

		absR = abs(r)
		if (r > 0):
			ang1 = int(-1*math.degrees(math.atan(d1/(abs(r)+d3))))
			ang2 = int(math.degrees(math.atan(d2/(abs(r)+d3))))
			ang3 = int(math.degrees(math.atan(d2/(abs(r)-d3))))
			ang4 = int(-1*math.degrees(math.atan(d1/(abs(r)-d3))))
		elif (r < 0):
			ang1 = int(1*math.degrees(math.atan(d1/(abs(r)-d3))))
			ang2 = -int(math.degrees(math.atan(d2/(abs(r)-d3))))
			ang3 = -int(math.degrees(math.atan(d2/(abs(r)+d3))))
			ang4 = int(1*math.degrees(math.atan(d1/(abs(r)+d3))))
		else:
			ang1,ang2,ang3,ang4 = 0,0,0,0

		return [ang1,ang2,ang3,ang4]

	#Sets the desired speed for each corner motor to turn at
	def turnCornerMotor(self):
		while (self.encoders[0] == None or \
				self.encoders[1] == None or \
				self.encoders[2] == None or \
				self.encoders[3] == None
				):
			time.sleep(0.01)
		counter,last_enc,deg = 0,-999,0

		for motorID in range(4):
			#if the rover isn't moving it can't turn its' wheels, to reduce ground friction on the corners
			if (self.__linear_speed != 0):
				deg = self.__tar_deg[motorID]
			enc = self.encoders[motorID]
			last_enc = enc
			self.__motor_speeds[motorID] = self.__calculateCornerSpeed(deg,enc,last_enc,counter)

	#Calculates how fast each corner motor should turn based on how far from target it is
	@staticmethod
	def __calculateCornerSpeed(deg,enc,last_enc,counter):
		#software limit of 43 deg
		if (deg > 43): deg = 43
		elif (deg < -43): deg = -43

		if (abs(enc-deg) > 30): speed = 60
		elif (abs(enc-deg) > 20): speed = 50
		elif (abs(enc-deg) > 10): speed = 45
		elif (abs(enc-deg) > 5): speed = 35
		else: speed = 0

		if (abs(last_enc - enc) < 5  and abs(enc-deg) > 10): counter+=1
		else: counter = 0

		#speed multiplier in case stalled on a physical object
		if counter > 10: speed = min(speed + int(counter/2), 70)
		if (enc > deg): speed = -1 * speed

		return speed

	#Calculates the angle that a corner motor is at, based on the scalings for that corner

	def getScaledEnc(self):
			encoders = [0]*4
			for i in range(4):
				if (i % 2):
					enc = self.rc.ReadEncM2(self.address[int(math.ceil((i+1)/2.0)+2)])[1]
				else:
					enc = self.rc.ReadEncM1(self.address[int(math.ceil((i+1)/2.0)+2)])[1]
				encoders[i] = int(cals[i][0] * math.pow(enc,2) + cals[i][1]*enc + cals[i][2])
			return encoders

	#Calculates the speed to distribute to each individual drive wheel based on geometry and turning radius
	@staticmethod
	def __getVelocity(r,speed):
		if (r == 0 or r >= 250 or r <= -250):
			#drive straight forward, all wheels move the same speed
				return [speed] * 6
		else:
			x = speed/(abs(r) + d4) #wheels can't move faster than max (127)
			a = math.pow(d2,2)
			b = math.pow(d3,2)
			c = math.pow(abs(r) + d1,2)
			d = math.pow(abs(r) - d1,2)
			e = abs(r) - d4


			v1 = int(x*math.sqrt(b + d))
			v2 = int(x*e)
			v3 = int(x*math.sqrt(a + d))
			v4 = int(x*math.sqrt(a + c))
			v5 = int(speed) #fastest wheel
			v6 = int(x*math.sqrt(b + c))

			if (r > 0):
				velocity = [v1,v2,v3,v4,v5,v6]
			elif (r < 0):
				velocity = [v6,v5,v4,v3,v2,v1]
			return velocity
	#Sets the speed of all 10 motors to 0
	def killMotors(self):
		for i in range(0,10):
			self.spinMotor(i,0)


	def drive(self,v):
		for i in range(6):
			self.spinMotor(i+4,v[i])


	def spinCorner(self, tar_enc):
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
		print 'x is:',   x
		speed, accel = 500,500
	
		self.rc.SpeedAccelDeccelPositionM1(self.address[3],accel,speed,accel,x[0],1)
		self.rc.SpeedAccelDeccelPositionM2(self.address[3],accel,speed,accel,x[1],1)
		self.rc.SpeedAccelDeccelPositionM1(self.address[4],accel,speed,accel,x[2],1)
		self.rc.SpeedAccelDeccelPositionM2(self.address[4],accel,speed,accel,x[3],1)


	#Wrapper function to spin each motor with an easier method call
	def spinMotor(self, motorID, speed):
		#serial address of roboclaw
		address = self.address
		rc = self.rc
		addr = {0: address[3],
				1: address[3],
				2: address[4],
				3: address[4],
				4: address[0],
				5: address[0],
				6: address[1],
				7: address[1],
				8: address[2],
				9: address[2]}

		#drive forward
		if (speed >= 0):
			command = {0: rc.ForwardM1,
					   1: rc.ForwardM2,
					   2: rc.ForwardM1,
					   3: rc.ForwardM2,
					   4: rc.ForwardM1,
					   5: rc.BackwardM2, #some are backward based on wiring diagram
					   6: rc.ForwardM1,
					   7: rc.ForwardM2,
					   8: rc.BackwardM1,
					   9: rc.ForwardM2}
		#drive backward
		else:
			command = {0: rc.BackwardM1,
					   1: rc.BackwardM2,
					   2: rc.BackwardM1,
					   3: rc.BackwardM2,
					   4: rc.BackwardM1,
					   5: rc.ForwardM2,
					   6: rc.BackwardM1,
					   7: rc.BackwardM2,
					   8: rc.ForwardM1,
					   9: rc.BackwardM2}

		speed = abs(speed)
		return command[motorID](addr[motorID],speed)


	def testMode(self):
		print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
		print "             Entering Motor Test Mode                   "
		print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
		print "             ** Type 'quit' to exit**                     "
		while True:
			sigs = raw_input("Input Drive speed and Steering amount: ")
			if (sigs == "quit"):
				print "\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
				print "             Exiting Motor Test Mode                    "
				print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
				self.turn_radius = 0
				time.sleep(1)
				self.drive_speed = 0
				print "Stopping Motors"
				time.sleep(1)
				myRover.killMotors()
				myRover.thread_kill = True
				return
			if len(sigs.split(" ")) == 2:
				v,s = sigs.split(" ")
				v,s = int(v),int(s)
				if (-100 <= v <= 100 and -100 <= s <=100):
					self.drive_speed = v
					self.turn_radius = s
					#self.driveController(myRover)
				else:
					print "Please enter numbers between -100 and 100"
			else:
				print "Please enter two numbers between -100 and 100 each, seperated with a space"

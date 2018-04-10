#!/usr/bin/env python
import time
import serial
import math
from roboclaw import Roboclaw
import config

d1,d2,d3,d4 = config.d1,config.d2,config.d3,config.d4
cals = config.cals

class Rover():
	def __init__(self):
		self.rc = Roboclaw("/dev/ttyS0",115200)
		self.rc.Open()
		self.address = [0x80,0x81,0x82,0x83,0x84]
		self.rc.ResetEncoders(self.address[0])
		self.rc.ResetEncoders(self.address[1])
		self.rc.ResetEncoders(self.address[2])


	def getScaledEnc(self):
			encoders = [0]*4
			for i in range(4):
				if (i % 2):
					enc = self.rc.ReadEncM2(self.address[int(math.ceil((i+1)/2.0)+2)])[1]
				else:
					enc = self.rc.ReadEncM1(self.address[int(math.ceil((i+1)/2.0)+2)])[1]
				encoders[i] = int(cals[i][0] * math.pow(enc,2) + cals[i][1]*enc + cals[i][2])
			return encoders

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

		return [ang2,ang1,ang4,ang3]

	def calculateDriveSpeed(self,v,cur_rad):
		v = int(v)*(127/100)
		if (v == 0):
			return [0]*6
		else:
			return  self.__getVelocity(cur_rad,v)

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

			if (r < 0):
				velocity = [v1,v2,v3,v4,v5,v6]
			elif (r > 0):
				velocity = [v6,v5,v4,v3,v2,v1]
			return velocity

	def killMotors(self):
		for i in range(0,10):
			self.spinMotor(i,0)


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
				else:
					x[i] = int(x2)          #I don't think this case can ever happen. 
		speed, accel = 1000,2000
		self.rc.SpeedAccelDeccelPositionM1(self.address[3],accel,speed,accel,x[0],1)
		self.rc.SpeedAccelDeccelPositionM2(self.address[3],accel,speed,accel,x[1],1)
		self.rc.SpeedAccelDeccelPositionM1(self.address[4],accel,speed,accel,x[2],1)
		self.rc.SpeedAccelDeccelPositionM2(self.address[4],accel,speed,accel,x[3],1)


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

	def drive(self,v,r):
		current_radius = self.getTurningRadius(self.getScaledEnc())
		velocity = self.calculateDriveSpeed(v, current_radius)
		self.spinCorner(self.calculateCornerAngles(r))
		for i in range(6):
			self.spinMotor(i+4,velocity[i])

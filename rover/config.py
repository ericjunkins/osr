#!/usr/bin/env python

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Modify these scalings after calibrating the corner steering
# encoders, this is VERY important for the rover to turn properly
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Calibration Scalings for corner motor absolute encoders
e1_scaling = [1E-06, 0.0609, -58.6]
e2_scaling = [2E-05, 0.0275, -68.668]
e3_scaling = [3E-05,-0.0069, -47.755]
e4_scaling = [8E-05,-0.0621, -32.147]

cals = [e1_scaling,e2_scaling,e3_scaling,e4_scaling]

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Modify these distances only if you have changed some of the
# mechanical distances between wheels in your rover geometry
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# x distance from middle of rover to the corner wheels 
d1 = 7.254

# y distance from middle wheel to back corner wheels
d2 = 10.5

# y distance from middle wheel to front corner wheels
d3 = 10.5

# x distance from middle of rover to middle wheel
d4 = 10.073


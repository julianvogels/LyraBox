#!/usr/bin/env python

import mapper, sys
import math

# function to receive a signal through libmapper
def h(sig, id, f, timetag):
	try:
		print sig.name, f
	except:
		print 'exception'
		print sig, f

dev = mapper.device("Lyrabox", 9000)
sig1 = dev.add_output("/button", 1, 'i', None, 0, 1)
sig2 = dev.add_output("/switch1", 1, 'i', None, 0, 1)
sig3 = dev.add_output("/switch2", 1, 'i', None, 0, 1)
sig4 = dev.add_output("/encoder", 1, 'i', None, 0, 1)
sig5 = dev.add_output("/enc_button", 1, 'i', None, 0, 1)
sig6 = dev.add_output("/analog_sensor0", 1, 'f', None, 0, 1024)
sig_in = dev.add_input("/led", 1, 'i', "normalized", 0, 1, h)


# function to update the libmapper signal
#	usage: signal number (int), sinal value (whatever is in range)
def updateSignal(signal, value):
	if signal==1:
		sig1.update(value)

	if signal==2:
		sig2.update(value)
		
	if signal==3:
		sig3.update(value)
		
	if signal==4:
		sig4.update(value)
		
	if signal==5:
		sig5.update(value)
		
	if signal==6:
		sig6.update(value)

def do_poll():
    dev.poll(0)

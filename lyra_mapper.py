#!/usr/bin/env python

import mapper
import math


class LyraMapper():

	# function to receive a signal through libmapper
	def h(sig, id, f, timetag):
    try:
        print sig.name, f
    except:
        print 'exception'
        print sig, f

	# function called on initialization
	def __init__(self):
		s = Server().boot()
		s.start()
		try:
			self.dev = mapper.device("Lyrabox", 9000)
			self.sig1 = self.dev.add_output("/button", 1, 'i', "normalized", 0, 1)
			self.sig2 = self.dev.add_output("/switch1", 1, 'i', "normalized", 0, 1)
			self.sig3 = self.dev.add_output("/switch2", 1, 'i', "normalized", 0, 1)
			self.sig4 = self.dev.add_output("/encoder", 1, 'i', "normalized", 0, 1)
			self.sig5 = self.dev.add_output("/enc_button", 1, 'i', "normalized", 0, 1)
			self.sig6 = self.dev.add_output("/analog_sensor0", 1, 'f', "normalized", 0, 1024)
			self.sig7 = self.dev.add_input("/led", 1, 'i', "normalized", 0, 1, h)
			while True:
				dev.poll(0)
		finally:
			s.stop()

	# function to update the libmapper signal
	#	usage: signal number (int), sinal value (whatever is in range)
	def updateSignal(signal, value):
		if signal==1:
			self.sig1.update(value)

		if signal==2:
			self.sig2.update(value)
			
		if signal==3:
			self.sig3.update(value)
			
		if signal==4:
			self.sig4.update(value)
			
		if signal==5:
			self.sig5.update(value)
			
		if signal==6:
			self.sig6.update(value)




	
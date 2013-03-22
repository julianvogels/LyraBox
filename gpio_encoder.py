#!/usr/bin/env python
import time
import os

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

import gaugette.rotary_encoder
import gaugette.switch

#LIBMAPPER IMPORT
from lyra_mapper import LyraMapper

lyra_mapper = LyraMapper()

class LyraIO():

    def __init__(self):
        #======================================
        #   GENERAL CONFIGURATION
        #======================================
        DEBUG = 1

        if DEBUG:
            print "RaspberryPi Board Revision: ", GPIO.RPI_REVISION
            print "GPIO version", GPIO.VERSION

        GPIO.setmode(GPIO.BOARD)

        sampling_frequency = 50.0
        sampling_period = 1.0/sampling_frequency

        #======================================
        #   PIN CONFIGURATION
        #======================================

        #============
        # ROTARY ENCODER PINS (BCM PIN NUMBERING!!!!!)
        #============
        A_PIN  = 7
        B_PIN  = 9
        # ENCODER PUSHBUTTON
        # ON MISO
        ENC_BUTTON = 21

        #============
        # MCP3008 ADC PINS
        #============
        # change these as desired - they're the pins connected from the
        # SPI port on the ADC to the Cobbler
        SPICLK = 12     #18 BCM
        SPIMISO = 16    #23
        SPIMOSI = 18    #24
        SPICS = 22      #25

        #============
        # SWITCH PINS
        #============
        # STATE ONE ON GPIO2 / R1R2
        SWITCH1 = 13
        # STATE TWO ON GPIO3
        SWITCH2 = 15

        #============
        # LED
        #============
        # ON GPIO17
        LED = 11

        #============
        # ARCADE BUTTON
        #============
        # ON MOSI
        BUTTON = 19

        #======================================
        #   DIGITAL READS CONFIGURATION
        #======================================
        GPIO.setup(SWITCH1, GPIO.IN)
        GPIO.setup(SWITCH2, GPIO.IN)
        GPIO.setup(LED, GPIO.OUT)
        GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ENC_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # EVENT CALLBACK FUNCTIONS

        def button_callback():
            print('Button press HIGH')

        def switch1_callback():
            print('Switch 1 state change HIGH')

        def switch2_callback():
            print('Switch 2 state change HIGH')

        def enc_button_callback():
            print('Encoder button press HIGH')

        def read_switch():
            val1 = GPIO.input(SWITCH1)
            val2 = GPIO.input(SWITCH2)
            return val1;
            # TODO edge detection

        def read_button():
            button_state = GPIO.input(BUTTON)
            return button_state

        def write_led(led_state):
            if (led_state == True):
                GPIO.output(LED, GPIO.HIGH)
            else:
                GPIO.output(LED, GPIO.LOW)

        GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=button_callback)  
        GPIO.add_event_detect(SWITCH1, GPIO.RISING, callback=switch1_callback)  
        GPIO.add_event_detect(SWITCH2, GPIO.RISING, callback=switch2_callback)
        GPIO.add_event_detect(ENC_BUTTON, GPIO.RISING, callback=enc_button_callback)  

        #======================================
        #   ENCODER CONFIGURATION
        #======================================

        encoder = gaugette.rotary_encoder.RotaryEncoder.Worker(A_PIN, B_PIN)
        encoder.start()

        # read data from rotary encoder using gaugette lib
        def read_encoder():
            return encoder.get_delta()

        #======================================
        #   MCP3008 ADC CONFIGURATION
        #======================================

        # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
        def read_adc(adcnum, clockpin, mosipin, misopin, cspin):
                if ((adcnum > 7) or (adcnum < 0)):
                        return -1
                GPIO.output(cspin, True)

                GPIO.output(clockpin, False)  # start clock low
                GPIO.output(cspin, False)     # bring CS low

                commandout = adcnum
                commandout |= 0x18  # start bit + single-ended bit
                commandout <<= 3    # we only need to send 5 bits here
                for i in range(5):
                        if (commandout & 0x80):
                                GPIO.output(mosipin, True)
                        else:
                                GPIO.output(mosipin, False)
                        commandout <<= 1
                        GPIO.output(clockpin, True)
                        GPIO.output(clockpin, False)

                adcout = 0
                # read in one empty bit, one null bit and 10 ADC bits
                for i in range(12):
                        GPIO.output(clockpin, True)
                        GPIO.output(clockpin, False)
                        adcout <<= 1
                        if (GPIO.input(misopin)):
                                adcout |= 0x1

                GPIO.output(cspin, True)
                
                adcout >>= 1       # first bit is 'null' so drop it
                return adcout

        # set up the SPI interface pins
        GPIO.setup(SPIMOSI, GPIO.OUT)
        GPIO.setup(SPIMISO, GPIO.IN)
        GPIO.setup(SPICLK, GPIO.OUT)
        GPIO.setup(SPICS, GPIO.OUT)

        # SHARP Infrared Sensor connected to adc #0
        sensor0_adc_pin = 0;

        adc_last_state = 0      # this keeps track of the last potentiometer value
        tolerance = 5           # to keep from being jittery only change
                                # libm_sensor0_val when sensor has moved more than 5 'counts'
                                # NOTE: NOT USED, will be handled in PureData

        # main loop for sensor measurement
        while True:
                #======================================
                #   DIGITAL READING
                #======================================

                # ! EDGE DETECTION IS USED TO LOWER CPU USAGE AND AVOID MISSING STATE CHANGES

                # libm_button_val = read_button()
                # write_led(libm_button_val)
                # if DEBUG:
                #     print "Button State: ", libm_button_val

                # libm_switch_val = read_switch()
                # if DEBUG:
                #     print "Switch State: ", libm_switch_val


                #======================================
                #   ROTARY ENCODER READING
                #======================================
                libm_encoder_val = read_encoder()
                if DEBUG:
                    if libm_encoder_val!=0:
                        print "Encoder Direction: ", libm_encoder_val

                #======================================
                #   MCP3008 ADC READING
                #======================================

                # we'll assume that the pot didn't move
                analog_sensor0_changed = False

                # read the analog pin
                analog_sensor0 = read_adc(sensor0_adc_pin, SPICLK, SPIMOSI, SPIMISO, SPICS)
                # how much has it changed since the last read?
                sensor0_adjust = abs(analog_sensor0 - adc_last_state)

                if DEBUG:
                        pass
                        #print "analog_sensor0:", analog_sensor0
                        #print "sensor0_adjust:", sensor0_adjust
                        #print "adc_last_state", adc_last_state

                if ( sensor0_adjust > tolerance ):
                       analog_sensor0_changed = True

                if DEBUG:
                        pass
                        #print "analog_sensor0_changed", analog_sensor0_changed

                if ( analog_sensor0_changed ):
                        libm_sensor0_val = analog_sensor0 / 8.0           # convert 10bit adc0 (0-1024) sensor read into 0-127 MIDI std
                        
                        # DO STUFF


                        if DEBUG:
                                pass
                                #print "Calculated value: ", libm_sensor0_val

                # save the sensor reading for the next loop
                adc_last_state = analog_sensor0
                # hang out and do nothing for the sampling period
                # time.sleep(sampling_period)
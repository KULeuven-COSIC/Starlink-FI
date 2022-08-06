import numpy as np
import time
import serial
from tqdm import tnrange, tqdm
import random
from pulsegen import PicoPulseGen

# Open serial interface
# I'm using this to detect when the glitch was successful
try:
	ser = serial.Serial('/dev/ttyUSB0', 115200)

except Exception as e:
	print('Could not open /dev/ttyUSB0')
	exit()

# Connect to modchip
try:
	glitcher = PicoPulseGen('/dev/ttyACM0')
	logger.info('Connected to modchip')

	# You have to figure out the trig_edges parameter
	# You have to figure out ranges for the pulse_offset and pulse_width parameters
	glitcher.trig_edges = 0
	glitcher.pulse_offset = 0
	glitcher.pulse_width = 0
	glitcher.set_gpio(0)

except Exception as e:
	print('Could not connect to modchip')
	exit()

input("Press enter to start.")

def generator():
	while True:
		yield

idx = 0
success = False
for _ in tqdm(generator()):
	if idx % 10 == 0:
		# Pulse width and offset are expressed in number of cycles of the PIO state machine operating frequency (default in the provided fw is 250MHz).
		glitch_width = random.randint(A, B) # You have to figure out good ranges here
		glitch_offset = random.randint(C, D)

		glitcher.pulse_offset = glitch_offset
		glitcher.pulse_width = glitch_width
		
	ser.reset_input_buffer()
	glitcher.arm()			# Arm the modchip, it will try to power up the UT and will wait for the number of set trigger pulses to occur before inserting a glitch
	glitcher.wait_trig(timeout=5)	# Waits for the modchip to signal it has triggered. The modchip will be disarmed if no glitch has occurred within 5 seconds.
	
	time.sleep(0.55) # Have to wait for the second stage to start to see serial output
	data = ser.read(ser.in_waiting)
	
	if b'LENNERT' in data: # a check to determine if the glitch was successful. My BL2 has been modified to print LENNERT.
		success = True
		break
			
	glitcher.set_gpio(0) # Disables the core voltage regulator. The modchip firmware will re-enable the regulator automatically on the next glitch attempt.
	time.sleep(0.1)

	idx += 1

if success:
	print('Glitch successul!')
	logger.debug('%d, %d, %d' %(idx, glitch_width, glitch_offset))
	logger.debug(data.decode('utf-8', 'ignore'))

ser.close()
glitcher.close()
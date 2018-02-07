import serial
import serial.tools.list_ports
#import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import time
import datetime
import collections
import sys


ORANGE = '#ffa500'

ser = serial.Serial('/dev/ttyUSB0',9600)
print(ser.name)


plt.ion()
plt.style.use('dark_background')

class CO2Sensor:

	def __init__(self, serial_port_name = None):

		if not serial_port_name:
			ports = serial.tools.list_ports.comports()

			print("Found the following serial ports:")
			for port in ports:
				print("\t" + port.device)

			if len(ports) == 0:
				print('No Serial ports found')
				sys.exit(1)

			serial_port_name = ports[0].device

			print("Using: " + serial_port_name)

		self.serial_port_name = serial_port_name
		self.serial = serial.Serial(serial_port_name, 9600)

	def read(self):
		self.serial.write(bytes([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79]))
		response = self.serial.read(9)
		reading = int(response[2])*256 + int(response[3])

		return reading

class RealTimePlot:
	def __init__(self, depth = 5000, critical_level = 1000, warning_level = 700):
		self.critical_level = critical_level
		self.warning_level = warning_level
		self.fig, self.axes = plt.subplots()

		self.line, = self.axes.plot([], [], 'w')
		self.green_line, = self.axes.plot([], [], 'g')
		self.orange_line, = self.axes.plot([], [], ORANGE)
		self.red_line, = self.axes.plot([], [], 'r')
		self.axes.grid(color = (0.3 ,0.3 ,0.3))
		mng = plt.get_current_fig_manager()

		self.samples = collections.deque(maxlen = depth)
		self.timestamps = collections.deque(maxlen = depth)
		self.fig.autofmt_xdate()
		self.reading = self.fig.text(0.5, 0.95, 'Reading', ha='center', va='top', size='xx-large')
		self.warning = self.fig.text(0.5, 0.85, '', ha='center', va='top', size='xx-large', color='r')

	def add_sample(self, sample, timestamp):
		self.samples.append(sample)
		self.timestamps.append(timestamp)

	def update(self):
		self.set_reading()
		self.set_warnings()
		self.plot()

	def set_reading(self):
		reading = self.samples[-1]
		reading_text = r"CO$_2$: {} ppm".format(reading)
		self.reading.set_text(reading_text)
		#self.reading.draw()

	def set_warnings(self):
		reading = self.samples[-1]
		if reading > self.critical_level:
			self.fig.set_facecolor('r')
			self.warning.set_text(r'$\rightarrow$ OPEN WINDOW $\leftarrow$')

		elif reading > self.warning_level:
			self.fig.set_facecolor(ORANGE)
			self.warning.set_text('')

		else:
			self.fig.set_facecolor('g')
			self.warning.set_text('')

	def plot(self):

		green_data = list()
		green_timestamps = list()
		orange_data = list()
		orange_timestamps = list()
		red_data = list()
		red_timestamps = list()

		for i in range(len(self.samples)):
			if self.samples[i] > self.critical_level:
				red_data.append(self.samples[i])
				red_timestamps.append(self.timestamps[i])
				orange_data.append(self.samples[i])
				orange_timestamps.append(self.timestamps[i])
				green_data.append(self.samples[i])
				green_timestamps.append(self.timestamps[i])

			elif self.samples[i] > self.warning_level:
				red_data.append(None)
				red_timestamps.append(self.timestamps[i])
				orange_data.append(self.samples[i])
				orange_timestamps.append(self.timestamps[i])
				green_data.append(self.samples[i])
				green_timestamps.append(self.timestamps[i])

			else:
				red_data.append(None)
				red_timestamps.append(self.timestamps[i])
				orange_data.append(None)
				orange_timestamps.append(self.timestamps[i])
				green_data.append(self.samples[i])
				green_timestamps.append(self.timestamps[i])

		self.green_line.set_data(green_timestamps, green_data)
		self.orange_line.set_data(orange_timestamps, orange_data)
		self.red_line.set_data(red_timestamps, red_data)

		#self.line.set_data(self.timestamps, self.samples)
		x_min = min(self.timestamps)
		x_max = max(self.timestamps)
		y_min = min(self.samples)
		y_max = max(self.samples)
		y_delta = y_max - y_min
		y_margin = y_delta / 10
		self.axes.set_xlim(x_min, x_max)
		self.axes.set_ylim(y_min - y_margin, y_max + y_margin)
		self.axes.relim()


sensor = CO2Sensor()
plot = RealTimePlot()

logfile = open('co2log.txt', 'a')

while True:
	sample = sensor.read()
	timestamp = datetime.datetime.now()
	epoch = int(time.time())

	logfile.write("{},{}\n".format(epoch, sample))
	logfile.flush()

	plot.add_sample(sample, timestamp)
	plot.update()
#	history.append(reading)
#	timestamps.append(datetime.datetime.now())
	print("reading = {}".format(sample))
#	plt.cla()
#	ax.plot(timestamps, history)
#	fig.autofmt_xdate()
	plt.pause(5)

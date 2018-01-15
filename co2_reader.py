import serial
#import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import time
import datetime
import collections

ORANGE = '#ffa500'

ser = serial.Serial('/dev/ttyUSB0',9600)
print(ser.name)


plt.ion()
plt.style.use('dark_background')


class CO2Sensor:

	def __init__(self, serial_port_name = '/dev/ttyUSB0'):
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
		self.line.set_data(self.timestamps, self.samples)
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

while True:
	sample = sensor.read()
	timestamp = datetime.datetime.now()

	plot.add_sample(sample, timestamp)
	plot.update()
#	history.append(reading)
#	timestamps.append(datetime.datetime.now())
	print("reading = {}".format(sample))
#	plt.cla()
#	ax.plot(timestamps, history)
#	fig.autofmt_xdate()
	plt.pause(5)

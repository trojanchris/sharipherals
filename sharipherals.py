from PyQt4 import QtGui
from PyQt4.QtCore import QThread, SIGNAL
import sys
import final_design as ui_design
from sharipherals_client import *
from sharipherals_server import *

def is_up(addr):
    """
    Checks if an ip address is up.

    :param addr: ip address to check
    :type addr: str
    """
    s = socket(AF_INET,SOCK_STREAM)
    s.settimeout(0.01)
    if not s.connect_ex((addr,135)):
        s.close()
        return 1
    else:
        s.close()

class getAvailableIps(QThread):

	def __init__(self):
		"""
		Make a new thread instance to check the
		connected network for possible hosts to
		connect to and return the hostname and 
		ip address.
		"""

		QThread.__init__(self)

	def __del__(self):
		self.wait()

	def run(self):
		"""
		Run the thread. This pulls the current
		machine's IP address and all findable
		ip addresses on the network.
		"""

		ip = gethostbyname(gethostname())
		if not ip:
			return False
		network = '.'.join(ip.split('.')[:3]) + '.'
		for ip in xrange(1,256):
			addr =  network + str(ip)
			if is_up(addr) and addr != gethostbyname(gethostname()):
				self.emit(SIGNAL('add_ip(QString)'), addr)

class connectServer(QThread):

	def __init__(self, ip):
		"""
		Make a new thread instance to connect
		to an ip addresses as the server
		peer.

		:param ip: client ip address to connect
		to
		:type ip: str
		"""

		self.ip = ip
		QThread.__init__(self)

	def __del__(self):
		self.wait()

	def run(self):
		p = SharipheralServer(self.ip, 7000)

class connectClient(QThread):

	def __init__(self):
		"""
		Make a new thread instance to connect
		to an ip addresses as the server
		peer.

		:param ip: client ip address to connect
		to
		:type ip: str
		"""
		QThread.__init__(self)

	def __del__(self):
		self.wait()

	def run(self):
		c = SharipheralClient()

class MainApplication(QtGui.QMainWindow, ui_design.Ui_MainWindow):
	"""
	The main application class. Creates the application
	window and registers all callbacks.
	"""

	def __init__(self):
		"""
		Initialized the application. Selects the server peer mode
		by default, registers signals and slots, and hides the
		client peer mode by default.
		"""

		super(self.__class__, self).__init__()
		self.setupUi(self)
		self.pushButton.clicked.connect(self.get_clients)
		self.pushButton_2.clicked.connect(self.connect_to_client)
		self.pushButton_3.clicked.connect(self.wait_for_connection)
		self.pushButton_3.hide()
		self.radioButton_2.setChecked(True)
		self.radioButton_2.toggled.connect(self.server_option_clicked)
		self.radioButton.toggled.connect(self.client_option_clicked)

	def get_clients(self):
		"""
		Creates and runs the thread to get all available client ip
		addresses on the local network. Registers callback for when
		a new ip address is found to add it to the list of possible
		clients to select from.
		"""

		self.get_thread = getAvailableIps()
		self.connect(self.get_thread, SIGNAL("add_ip(QString)"), self.add_ip)
		self.get_thread.start()

	def add_ip(self, ip):
		"""
		Add the text that's given to this function to the
		list of ips displayed to the server user.

		:param ip: text of the ip address to add to the drop down box
		:type ip: str
		"""

		self.comboBox.addItem(ip)

	def connect_to_client(self):
		"""
		Begins the client connection to the current selected ip
		in the drop down list.
		"""

		target_ip = str(self.comboBox.currentText())
		self.connect_thread = connectServer(target_ip)
		self.connect_thread.start()
		self.pushButton_2.setText('Connected')
		self.pushButton_2.setEnabled(False)

	def wait_for_connection(self):
		"""
		Waits for connection from server peer to receive
		inputs.
		"""

		self.wait_thread = connectClient()
		self.wait_thread.start()
		self.pushButton_3.setText('Waiting for input')
		self.pushButton_3.setEnabled(False)

	def server_option_clicked(self, enabled):
		"""
		Hides the client mode and displays the server mode options.
		"""

		if enabled:
			self.pushButton.show()
			self.comboBox.show()
			self.pushButton_2.show()
			self.pushButton_3.hide()
			self.label_2.show()
			self.label_3.show()

	def client_option_clicked(self, enabled):
		"""
		Hides the server mode and displays the client mode options.
		"""

		if enabled:
			self.pushButton.hide()
			self.comboBox.hide()
			self.pushButton_2.hide()
			self.pushButton_3.show()
			self.label_2.hide()
			self.label_3.hide()

def main():
	app = QtGui.QApplication(sys.argv)
	form = MainApplication()
	form.show()
	app.exec_()

if __name__ == '__main__':
	main()
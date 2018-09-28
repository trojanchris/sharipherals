from socket import socket, AF_INET, SOCK_DGRAM
import json, pythoncom, pyHook, time
from ctypes import windll, Structure, c_long, byref

class POINT(Structure):
	"""
	Generic structure for holding mouse position
	"""

	_fields_ = [
		("x", c_long),
		("y", c_long)
	]

def get_cursor_pos():
	"""
	Returns mouse position as a dict.
	"""

	pt = POINT()
	windll.user32.GetCursorPos(byref(pt))
	return { "x": pt.x, "y": pt.y }

class SharipheralServer():
	"""
	Server peer instance for sending keystrokes and mouse
	movements to a connected client peer.
	"""

	def __init__(self, ip, port):
		"""
		Initializes the server peer to a specific ip
		address and port. Registers hooks into all
		keystrokes and mouse movements, and switches
		to determine whether to send on to the client.

		:param ip: client ip address to connect to
		:type ip: str
		:param port: port at which to make the connection
		:type port: int
		"""

		self.ip = ip
		self.port = port
		self.hm = pyHook.HookManager()
		self.hm.KeyAll = self.hook_keys
		self.hm.HookKeyboard()
		self.hm.MouseAll = self.hook_mouse
		self.hm.HookMouse()
		self.switched1 = False
		self.switched2 = False
		self.switched3 = False
		self.socket = socket(AF_INET,SOCK_DGRAM)
		pythoncom.PumpMessages()

	def hook_keys(self, event):
		"""
		Callback for all keyboard events. Checks the event
		type and passess along keystrokes if mode is currently
		switched to send keystrokes to client peer.

		:param event: keyboard event
		:type event: dict
		"""

		if event.ScanCode == 29 and event.MessageName == 'key down':
			self.switched1 = True

		elif event.ScanCode == 42 and self.switched1 == True:
			self.switched2 = True

		else:
			self.switched1 = False
			self.switched2 = False
		
		if self.switched3:
			msg = json.dumps({'type':'key','event': event.MessageName, 'key': event.ScanCode})
			self.send_message(msg)
			return False

		return True

	def hook_mouse(self, event):
		"""
		Callback for all mouse events. Checks the event type
		and passes along mouse movements and clicks if mode
		is currently switched to send mouse events to client
		peer.

		:param event: mouse event
		:type event: dict
		"""

		set = False

		if event.MessageName == 'mouse right down' and self.switched2 == True:
			self.switched1 = False
			self.switched2 = False
			self.switched3 = not self.switched3
			if self.switched3 == False:
				msg = json.dumps({'type':'disconnect'})
				self.send_message(msg)
				self.x = None
				self.y = None
			else:
				self.set_cursor()

			set = True

		if self.switched3 and not set:
			x,y = event.Position[0], event.Position[1]
			msg = {'type':'mouse','event': event.MessageName,'x': x, 'y': y}
			if event.MessageName == 'mouse wheel':
				msg['wheel']=event.Wheel
			msg = json.dumps(msg)
			self.send_message(msg)
			if event.MessageName in ['mouse right down', 'mouse right up', 'mouse left down', 'mouse left up']:
				return False

		return True

	def set_cursor(self):
		"""
		Sets the current x and y coordinates of the mouse as an attribute
		of the instance.
		"""

		cur = get_cursor_pos()
		self.x = cur['x']
		self.y = cur['y']

	def send_message(self, message):
		"""
		Sends message to client peer via socket connection.

		:param message: Message to send
		:type message: str
		"""
		self.socket.sendto(message.encode('utf-8'), (self.ip, self.port))
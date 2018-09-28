import win32api, win32con, win32gui, win32process, win32clipboard
import ctypes
from socket import *
import json

SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
	_fields_ = [
		("wVk", ctypes.c_ushort),
		("wScan", ctypes.c_ushort),
		("dwFlags", ctypes.c_ulong),
		("time", ctypes.c_ulong),
		("dwExtraInfo", PUL)
	]

class HardwareInput(ctypes.Structure):
	_fields_ = [
		("uMsg", ctypes.c_ulong),
		("wParamL", ctypes.c_short),
		("wParamH", ctypes.c_ushort)
	]

class MouseInput(ctypes.Structure):
	_fields_ = [
		("dx", ctypes.c_long),
		("dy", ctypes.c_long),
		("mouseData", ctypes.c_ulong),
		("dwFlags", ctypes.c_ulong),
		("time",ctypes.c_ulong),
		("dwExtraInfo", PUL)
	]

class Input_I(ctypes.Union):
	_fields_ = [
		("ki", KeyBdInput),
		("mi", MouseInput),
		("hi", HardwareInput)
	]

class Input(ctypes.Structure):
	_fields_ = [
		("type", ctypes.c_ulong),
		("ii", Input_I)
	]

def PressKey(hexKeyCode):
	extra = ctypes.c_ulong(0)
	ii_ = Input_I()
	ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
	x = Input( ctypes.c_ulong(1), ii_ )
	ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
	extra = ctypes.c_ulong(0)
	ii_ = Input_I()
	ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
	x = Input( ctypes.c_ulong(1), ii_ )
	ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

class SharipheralClient():
	"""
	Client peer instance for receiving keystrokes and mouse movements
	from a server peer.
	"""

	def __init__(self):
		"""
		Initializes the instance and starts waiting for all incoming keystrokes/mouse
		movements through the default port of 7000. Executes the keystrokes/mouse
		movements as it receives them.
		"""

		self.hostName = gethostbyname('0.0.0.0')
		self.socket = socket(AF_INET, SOCK_DGRAM)
		self.socket.bind((self.hostName, 7000))
		pushed_keys = []
		last_down = None
		while True:
			(data, addr) = self.socket.recvfrom(1024)
			msg = json.loads(data)

			if msg['type'] == 'disconnect':
				for key in pushed_keys:
					ReleaseKey(key)
				pushded_keys = []

				if last_down:
					if last_down['event'] == 'mouse left down':
						win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, last_down['x'], last_down['y'])
					elif last_down['event'] == 'mouse right down':
						win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, last_down['x'], last_down['y'])
					last_down = None
				
			if msg['type'] == 'mouse':
				if msg['event'] == 'mouse left down':
					win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, msg['x'], msg['y'])
					last_down = msg
				elif msg['event'] == 'mouse left up':
					win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, msg['x'], msg['y'])
					last_down = None
				elif msg['event'] == 'mouse right down':
					win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, msg['x'], msg['y'])
					last_down = msg
				elif msg['event'] == 'mouse right up':
					win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, msg['x'], msg['y'])
					last_down = None
				elif msg['event'] == 'mouse wheel':
					if msg['wheel'] == 1:
						win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, x, y, 1, 0)
					else:
						win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, x, y, -1, 0)
				elif msg['event'] == 'mouse move':
					x,y = msg['x'], msg['y']
					ctypes.windll.user32.SetCursorPos(x,y)
			
			elif msg['type'] == 'key':
				if msg['event'] == 'key down':
					PressKey(msg['key'])
					pushed_keys.append(msg['key'])
				elif msg['event'] == 'key up':
					ReleaseKey(msg['key'])

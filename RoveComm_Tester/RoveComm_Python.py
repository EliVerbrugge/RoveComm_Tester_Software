import socket
import struct

ROVECOMM_PORT 			= 11000
ROVECOMM_VERSION 		= 2
ROVECOMM_HEADER_FORMAT 	= ">BHBB"

ROVECOMM_PING_REQUEST 			= 1
ROVECOMM_PING_REPLY				= 2
ROVECOMM_SUBSCRIBE_REQUEST 		= 3
ROVECOMM_UNSUBSCRIBE_REQUEST	= 4
ROVECOMM_INCOMPATIBLE_VERSION 	= 5

types_int_to_byte = {
	0: 'b',
	1: 'B',
	2: 'h',
	3: 'H',
	4: 'l',
	5: 'L',
	6: 'f',
}

types_byte_to_int = {
	'b': 0,
	'B': 1,
	'h': 2,
	'H': 3,
	'l': 4,
	'L': 5,
	'f': 6,
}


class RoveCommPacket:
	def __init__(self, data_id=0, data_type='b', data=(), ip_octet_4='', port=ROVECOMM_PORT):
		self.data_id = data_id
		self.data_type = data_type
		self.data_count = len(data)
		self.data = data
		if (ip_octet_4 != ''):
			self.ip_address = ('192.168.1.' + ip_octet_4, port)
		else:
			self.ip_address = ('0.0.0.0', port)
		return
	
	def SetIp(self, address):
		self.ip_address = (address, self.ip_address[1])
	
	def print(self):
		print('----------')
		print('{0:6s} {1}'.format('ID:', self.data_id))
		print('{0:6s} {1}'.format('Type:', self.data_type))
		print('{0:6s} {1}'.format('Count:', self.data_count))
		print('{0:6s} {1}'.format('IP:', self.ip_address))
		print('{0:6s} {1}'.format('Data:', self.data))
		print('----------')
	
	
class RoveCommEthernetUdp:
	def __init__(self, port=ROVECOMM_PORT):
		self.rove_comm_port = port
		self.subscribers = []
	
		self.RoveCommSocket = socket.socket(type=socket.SOCK_DGRAM)
		self.RoveCommSocket.setblocking(False)
		self.RoveCommSocket.bind(("", self.rove_comm_port))
	
	def write(self, packet):
		try:
			packet.print()
			if not isinstance(packet.data, tuple):
				raise ValueError('Must pass data as a tuple, Data: ' + str(packet.data))

			rovecomm_packet = struct.pack(ROVECOMM_HEADER_FORMAT, ROVECOMM_VERSION, packet.data_id, packet.data_count,
										  types_byte_to_int[packet.data_type])
			for i in packet.data:
				rovecomm_packet = rovecomm_packet + struct.pack('>' + packet.data_type, i)

			for subscriber in self.subscribers:
					self.RoveCommSocket.sendto(rovecomm_packet, (subscriber))
			
			if (packet.ip_address != ('0.0.0.0', 0) and not (packet.ip_address in self.subscribers)):
				self.RoveCommSocket.sendto(rovecomm_packet, packet.ip_address)

			return 1
		except:
			return 0

	def read(self):
		try:
			packet, remote_ip = self.RoveCommSocket.recvfrom(1024)
			header_size = struct.calcsize(ROVECOMM_HEADER_FORMAT)
	
			rovecomm_version, data_id, data_count, data_type = struct.unpack(ROVECOMM_HEADER_FORMAT, packet[0:header_size])
			data = packet[header_size:]
	
			if(rovecomm_version != 2):
				returnPacket = RoveCommPacket(ROVECOMM_INCOMPATIBLE_VERSION, 'b', (1,), '')
				returnPacket.ip_address = remote_ip
				return returnPacket
	
			if (data_id == ROVECOMM_SUBSCRIBE_REQUEST):
				if (self.subscribers.count(remote_ip) == 0):
					self.subscribers.append(remote_ip)
			elif (data_id == ROVECOMM_UNSUBSCRIBE_REQUEST):
				if (self.subscribers.count(remote_ip) != 0):
					self.subscribers.remove(remote_ip)
	
			data_type = types_int_to_byte[data_type]
			data = struct.unpack('>' + data_type * data_count, data)
	
			returnPacket = RoveCommPacket(data_id, data_type, data, '')
			returnPacket.ip_address = remote_ip
			return returnPacket
	
		except:
			returnPacket = RoveCommPacket()
			return (returnPacket)

class RoveCommEthernetTCP:
	def __init__(self):
		self.open_sockets = {}
	
	def write(self, packet):
		try:
			packet.print()
			if not isinstance(packet.data, tuple):
				raise ValueError('Must pass data as a tuple, Data: ' + str(data))

			rovecomm_packet = struct.pack(ROVECOMM_HEADER_FORMAT, ROVECOMM_VERSION, packet.data_id, packet.data_count,
										  types_byte_to_int[packet.data_type])
			for i in packet.data:
				rovecomm_packet = rovecomm_packet + struct.pack('>' + packet.data_type, i)
			
			#establish a new connection if the server has not yet been connected to
			self.connect(packet.ip_address)

			if (packet.ip_address != ('0.0.0.0', 0)):
				self.open_sockets[packet.ip_address].send(rovecomm_packet)
				return 1
		except:
			return 0

	def connect(self, ip_address):
		if not ip_address in self.open_sockets:
			TCPSocket = socket.socket(type=socket.SOCK_STREAM)
			try:
				TCPSocket.connect(ip_address)
			except Exception as e: 
				print("something's wrong. Exception is %s" % (e))
			self.open_sockets[ip_address] = TCPSocket

	def read(self, RoveComm_Socket):
		try:
			packet, remote_ip = RoveComm_Socket.recvfrom(1024)
			header_size = struct.calcsize(ROVECOMM_HEADER_FORMAT)
	
			rovecomm_version, data_id, data_count, data_type = struct.unpack(ROVECOMM_HEADER_FORMAT, packet[0:header_size])
			data = packet[header_size:]
	
			if(rovecomm_version != 2):
				returnPacket = RoveCommPacket(ROVECOMM_INCOMPATIBLE_VERSION, 'b', (1,), '')
				returnPacket.ip_address = remote_ip
				return returnPacket
	
			data_type = types_int_to_byte[data_type]
			data = struct.unpack('>' + data_type * data_count, data)
	
			returnPacket = RoveCommPacket(data_id, data_type, data, '')
			returnPacket.ip_address = remote_ip
			return returnPacket
	
		except Exception as e: 
			returnPacket = RoveCommPacket()
			return (returnPacket)

# def readFrom ToDo: Change to getLastIp for C++ and Python

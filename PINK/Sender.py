import sys
import struct
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from RoveComm_Python import *

RoveComm = RoveCommEthernetUdp()

types_text_to_byte  = {
						'Int8':'b',
						'uInt8':'B',
						'Int16':'h',
						'uInt16':'H',
						'Int32':'l',
						'uInt32':'L',
					  }

class Sender(QWidget):
	
	def __init__(self):
		super().__init__()
		
		self.initUI()
		
	def initUI(self):	
		exitAct = QAction(QIcon('exit.png'), '&Exit', self)        
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setStatusTip('Exit application')
		exitAct.triggered.connect(qApp.quit)
		
		#used with QMainWindow
		#menubar = self.menuBar()
		#fileMenu = menubar.addMenu('&File')
		#fileMenu.addAction(exitAct)
		
		self.send_widgets = [sendWidget(self, 1)]
		
		self.main_layout=QVBoxLayout(self)
		self.main_layout.addWidget(self.send_widgets[0])
		
		self.setWindowTitle('Sender')
		self.setWindowIcon(QIcon('Rover.png')) 
		
		
		self.resize(self.sizeHint())

		self.show()
	def redrawWidgets(self):
		for i in range(0, len(self.send_widgets)):
			self.main_layout.removeWidget(self.send_widgets[i])
			self.main_layout.addWidget(self.send_widgets[i])
			self.send_widgets[i].setNumber(i+1)			
		
	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Escape:
			self.close()
	def addEvent(self, number):
		sender = self.sender()
		self.send_widgets = self.send_widgets[:number] + [sendWidget(self, len(self.send_widgets))] + self.send_widgets[number:]
		self.redrawWidgets()
		
	def removeEvent(self, number):
		sender = self.sender()
		self.main_layout.removeWidget(self.send_widgets[-1])
		self.send_widgets[number-1].deleteLater()
		self.send_widgets[number-1] = None
		self.send_widgets = self.send_widgets[:number-1] + self.send_widgets[number:]
		
		self.redrawWidgets()
		
class sendWidget(QWidget):
	def __init__(self, parent=None, number=1):
		QWidget.__init__(self, parent=parent)
		
		super(sendWidget, self).__init__(parent)
		self.initUI(parent, number)
		
	def initUI(self, parent, number):
		self.data_id_text = QLabel('Data ID', self)
		self.data_type_text = QLabel('Data Type', self)
		self.data_size_text = QLabel('Data Size', self)
		self.data_data_text = QLabel('Data', self)
		self.ip_octet_4_text = QLabel('IP Octet 4', self)
		
		self.number_txt = QLabel(str(number) + '.', self)
		self.number = number
		
		send = QPushButton('Send', self)
		send.resize(send.sizeHint())
		send.clicked.connect(self.sendEvent)
		
		add = QPushButton('Add', self)
		add.resize(send.sizeHint())
		add.clicked.connect(self.addEvent)
		
		remove = QPushButton('X', self)
		remove.resize(send.sizeHint())
		remove.clicked.connect(self.removeEvent)
		
		self.data_id_le     = QLineEdit(self)
		self.data_length_le = QLineEdit(self)
		self.ip_octet_4_le  = QLineEdit(self)
		
		self.data_length_le.textChanged[str].connect(self.data_length_entry)
		self.data_length = 1
		
		self.data_type_cb   = QComboBox(self)
		self.data_type_cb.addItem("Int8")
		self.data_type_cb.addItem("uInt8")
		self.data_type_cb.addItem("Int16")
		self.data_type_cb.addItem("uInt16")
		self.data_type_cb.addItem("Int32")
		self.data_type_cb.addItem("uInt32")
		
		self.data_array    = [QLineEdit(self)]
		
		self.main_layout=QGridLayout(self)
		self.main_layout.addWidget(self.data_id_text, 0, 3)
		self.main_layout.addWidget(self.data_type_text, 0, 4)
		self.main_layout.addWidget(self.data_size_text, 0, 5)
		self.main_layout.addWidget(self.data_data_text, 0, 6)
		self.main_layout.addWidget(self.ip_octet_4_text, 0, 7)
		
		self.main_layout.addWidget(self.number_txt, 1, 0)
		self.main_layout.addWidget(add, 1, 1)
		self.main_layout.addWidget(remove, 1, 2)
		self.main_layout.addWidget(self.data_id_le, 1, 3)
		self.main_layout.addWidget(self.data_type_cb, 1, 4)
		self.main_layout.addWidget(self.data_length_le, 1, 5)
		self.main_layout.addWidget(self.data_array[0], 1, 6)
		self.main_layout.addWidget(self.ip_octet_4_le, 1, 7)
		self.main_layout.addWidget(send, 1, 8)
		self.resize(self.sizeHint())
		
		self.show()

	def sendEvent(self):
		data = ( )
		for i in range(0, self.data_length):
			data = (data) + (int(self.data_array[i].text()),)
			
		packet = RoveCommPacket(int(self.data_id_le.text()), types_text_to_byte[self.data_type_cb.currentText()], data, self.ip_octet_4_le.text())
		RoveComm.write(packet)
				
	
	def addEvent(self, parent):
		self.parent().addEvent(self.number)
		
	def removeEvent(self, parent):
		self.parent().removeEvent(self.number)
	
	def setNumber(self, number):
		self.number = number
		self.number_txt.setText(str(number) + '.')
		
	def data_length_entry(self):
		sender = self.sender()
		try:
			new_length = int(sender.text())
			if(new_length>self.data_length):
				for i in range(self.data_length, new_length):
					self.data_array = self.data_array+[QLineEdit(self)]
					self.main_layout.addWidget(self.data_array[i], i+1, 6)
			elif(new_length<self.data_length):
				for i in range(self.data_length, new_length, -1):
					self.main_layout.removeWidget(self.data_array[-1])
					self.data_array[-1].deleteLater()
					self.data_array[-1] = None
					self.data_array = self.data_array[:-1]
			self.data_length = new_length
					
		except:
			return
	
if __name__ == '__main__':
	
	app = QApplication(sys.argv)
	ex = Sender()
	sys.exit(app.exec_())
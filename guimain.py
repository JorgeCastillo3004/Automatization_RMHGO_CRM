
import sys

from datetime import date
from database import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QFormLayout
)

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMessageBox

#### LOAD MODULES ###
from main import *

class Worker(QtCore.QObject):# BOT OR OBJECT TO BE MANIPULATE

    descargarSignal = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self._i = 0
        self._stop = False
    # ACTION OR PROCCESS TO MANIPULATE START OR STOP
    def activateFunction(self):
        def incAndEmit():
            self._i, self._stop = processControl(self._i, self._stop)
            self.descargarSignal.emit(self._stop)
        QtCore.QTimer.singleShot(100, incAndEmit)

class WindowMain(QWidget):

    cargarSignal = QtCore.pyqtSignal() # TO CONNECT WITHO OTHER PROCCESS OR OBJECT

    def __init__(self):
        super().__init__()
        # INICIALIZACION DE VENTANA ACTUAL
        self.fecha = date.today().strftime("%d/%m/%Y")        
        ############### Creacion de botones y elementos asociacion con funciones #################        
        
        self.ButtonUnread = QtWidgets.QPushButton('Unread')
        self.ButtonUnread.setFixedSize(150, 25)
        self.ButtonUnread.setCheckable(True)
        self.ButtonUnread.clicked.connect(self.ExecuteUnread)

        self.ButtonRecents = QtWidgets.QPushButton('Recents')
        self.ButtonRecents.setFixedSize(150, 25)
        self.ButtonRecents.setCheckable(True)
        self.ButtonRecents.clicked.connect(self.ExecuteRecents)

        self.ButtonStarred = QtWidgets.QPushButton('Starred')
        self.ButtonStarred.setFixedSize(150, 25)
        self.ButtonStarred.setCheckable(True)
        self.ButtonStarred.clicked.connect(self.ExecuteStarred)

        self.ButtonLoadConversation = QtWidgets.QPushButton('LoadConversation')
        self.ButtonLoadConversation.setFixedSize(150, 25)        
        self.ButtonLoadConversation.clicked.connect(self.ExecuteLoadConversation)

        # LAUNCH NAVIGATOR
        self.ButtonLaunchNavigator = QtWidgets.QPushButton('Launch Navigator')
        self.ButtonLaunchNavigator.setFixedSize(150, 25)
        self.ButtonLaunchNavigator.setCheckable(True)
        self.ButtonLaunchNavigator.clicked.connect(self.ExecuteLaunchNavigator)

        # START TO SEND MESSAGES
        # self.ButtonStart = QtWidgets.QPushButton('Start')
        # self.ButtonStart.setFixedSize(150, 25)
        # self.ButtonStart.setCheckable(True)
        # self.flag_stop = False
        # self.ButtonStart.clicked.connect(self.ExecuteStart)

        # STOP MESSAGE RESEND`
        self.ButtonStartPause = QtWidgets.QPushButton('Start')
        self.ButtonStartPause.setFixedSize(150, 25)        
        self.ButtonStartPause.clicked.connect(self.ExecuteStartPause)

        # STOP MESSAGE RESEND
        self.ButtonStop = QtWidgets.QPushButton('Stop')
        self.ButtonStop.setFixedSize(150, 25)
        self.ButtonStop.setCheckable(True)
        self.ButtonStop.clicked.connect(self.ExecuteStop)

        self.selectLoadMore = QtWidgets.QComboBox()        
        self.selectLoadMore.setFixedSize(150, 25)
        self.selectLoadMore.setObjectName("LoadMore")
        self.selectLoadMore.addItem("Load More")
        self.selectLoadMore.addItem("100")
        self.selectLoadMore.addItem("250")
        self.selectLoadMore.addItem("500")
        self.selectLoadMore.addItem("All")

        self.unread = QtWidgets.QCheckBox("Unread")
        self.unread.setCheckState(Qt.Checked)

        self.recents = QtWidgets.QCheckBox("Recents")
        self.recents.setCheckState(Qt.Checked)

        self.starred = QtWidgets.QCheckBox("Starred")
        self.starred.setCheckState(Qt.Checked)

        self.dbase = createConection()
        results = getMessagesIsues(self.dbase)
        nrows = len(results)        
        self.Table = TableUser(results, nrows, 6)
        
        SetInicio(self)

        ############## SECTION PROCESS CONTROL ###################
        worker = Worker()
        thread = QtCore.QThread()

        self.cargarSignal.connect(worker.activateFunction)  ###     LOAD INFO TO SECOND CLASS ###
        worker.descargarSignal.connect(self.cargarFunct)
        # self.retrieve.connect(worker.onRetrieve)
        # worker.retrieved.connect(self.onRetrieved)
        worker.moveToThread(thread)
        thread.start()

        self._thread = thread # protect from destroying by gc
        self._worker = worker # protect from destroying by gc
        self._stop = True
        ########################################################

    def ExecuteLaunchNavigator(self):
        launchNavigator()

    # def ExecuteStart(self):        
    #     self._stop = False
    #     self.retrieve.emit()

    def ExecuteStartPause(self):
        print("Button start pause", self._stop)        

        if self._stop:
            self.ButtonStartPause.setText("Pause") 
            self.ButtonStop.setChecked(False)
            print(" set text button pause ")
            print("Continuando verificacion ")
            self._stop = False
            self.cargarSignal.emit()

        else:
            self.ButtonStartPause.setText("Start")
            print(" set text button start")
            print("Precesso detenido")
            self._stop = True

        # self._stop = not(self._stop)
        # self.retrieve.emit()

    def ExecuteStop(self): 
        self.ButtonStartPause.setText("Start")
        self.ButtonStop.setChecked(True)
        self._stop = True

    ###################   FUNTION TO CONNECT ##################
    def cargarFunct(self, _stop): # $$$$$$$$$$$$$$$$$$$$$$$$$
        # process data
        if self._stop:
            # self._stop = _stop
            self.ButtonStartPause.setText("Start")
            return
        # self._i = Descargar._i
        else:
            self.cargarSignal.emit()
    # def onRetrieved(self, data):
    #     # process data
    #     print("onRetrieved", data)
    #     if self._stop:
    #         return
    #     # self.retrieve.emit()

    def ExecuteUnread(self):
        self.ButtonUnread.setChecked(True)
        self.ButtonRecents.setChecked(False)
        self.ButtonStarred.setChecked(False)
        self._i = 0

    def ExecuteRecents(self):
        self.ButtonRecents.setChecked(True)
        self.ButtonUnread.setChecked(False)        
        self.ButtonStarred.setChecked(False)
        self._i = 0
        loadRecents()

    def ExecuteStarred(self):
        self.ButtonStarred.setChecked(True)
        self.ButtonUnread.setChecked(False)
        self.ButtonRecents.setChecked(False)
        self._i = 0

    def ExecuteLoadConversation(self):
        numbload_txt= self.selectLoadMore.currentText()

        print("numbload_txt", numbload_txt)

        # try:print("Init try:")
        listnumb = re.findall(r'\d+', numbload_txt)
        if len(listnumb)!=0:
            numbload_ = int(listnumb[0])/20 - 1            
        else:
            if numbload_txt =='Load More':
                numbload_ = 3
            else:
                print("Load all")
                numbload_ = getTotalConversation()
        if numbload_ > 50:
            QMessageBox.about(self, "Maximum number of allowed conversations",
                "Please remember that it only permits loading a maximum of 100 times.") 
            numbload_ = 15
        print("Resulted number of load more:", numbload_)
        clickLoadMore(numbload = 2)


def SetInicio(self):
    #               LAYERS SETTING                      
    #####################################################
    #                                                   #
    #           FirstButtonlayout                       #
    #                                                   #
    #####################################################
    #                    #                              #
    #       SideButton   #      Table                   #
    #                    #                              #
    #                    #                              #
    #                    #                              #
    #                    #                              #
    #####################################################
	# CleanSideButtonTable(self)
	# MAIN LAYOUT VERTICAL#       
    self.Mainlayout = QVBoxLayout()

    # FIRST ROWS OF BUTTONS
    self.FirstButtonlayout = QHBoxLayout()

    # SIDE LAYOUT SETTED TO THE LEFT
    self.SideButton = QVBoxLayout()
    # LAYOUT FOR THE TABLE
    self.Tablelayout = QHBoxLayout()    

    # Add Buttons to Buttons layout    
    self.FirstButtonlayout.addWidget(self.ButtonLaunchNavigator, 0)
    self.FirstButtonlayout.addWidget(self.ButtonUnread, 0)
    self.FirstButtonlayout.addWidget(self.ButtonRecents, 0)
    self.FirstButtonlayout.addWidget(self.ButtonStarred, 0)
    self.FirstButtonlayout.addWidget(self.ButtonLoadConversation, 0)
    self.FirstButtonlayout.addWidget(self.selectLoadMore, 0)
    # Add table and side buttons to Table layout.
    self.Tablelayout.addLayout(self.SideButton)
    self.Tablelayout.addWidget(self.Table)

    # ADD ELEMENTS TO THE SIDEBUTTON LAYOUT    
    # self.SideButton.addWidget(self.ButtonStart)
    self.SideButton.addWidget(self.ButtonStartPause)
    self.SideButton.addWidget(self.ButtonStop)
    # self.SideButton.addWidget(self.selectLoadMore)
    self.SideButton.addWidget(self.unread)
    self.SideButton.addWidget(self.recents)
    self.SideButton.addWidget(self.starred)    

    # CREATE AND ADD VERTICAL SPACER TO LAYER SIDEBUTTONS
    self.VerticalSpacer = QFrame()
    self.VerticalSpacer.Shape(QFrame.VLine)
    self.VerticalSpacer.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Expanding)    
    self.SideButton.addWidget(self.VerticalSpacer)

    # ADD OTHERS LAYOUTS TO THE MAIN LAYOUT
    self.Mainlayout.addLayout(self.FirstButtonlayout)
    self.Mainlayout.addLayout(self.Tablelayout)
    self.setLayout(self.Mainlayout)
        
    self.setWindowTitle("RMH GO CONTROL")
    # self.setGeometry(100,100, 220, 260)

class TableUser(QTableWidget):
    def __init__(self, results, *args):
        QTableWidget.__init__(self, *args)        
        self.results = results
        self.setData()
        # self.resizeColumnsToContents()
        # self.resizeRowsToContents()
        self.header = self.horizontalHeader()
        # self.header.setStretchLastSection(True)

    def setData(self): 
        
        horHeaders = ['Name','Phone', 'Date','Time', 'Issues','State']
        # self.setColumnWidth(0, 100)
        # self.setColumnWidth(1, 110)
        # self.setColumnWidth(2, 85)
        # self.setColumnWidth(3, 60)
        # self.setColumnWidth(4, 50)
        # self.setColumnWidth(5, 30)
        
        for n, result in enumerate(self.results):

            for m, item in enumerate(result):

                newitem = QTableWidgetItem(str(item))
                newitem.setFlags(QtCore.Qt.ItemIsEnabled)                
                self.setItem( n, m, newitem)

        self.setHorizontalHeaderLabels(horHeaders)

if __name__ == "__main__":	
    app = QApplication(sys.argv)
    window = WindowMain()
    # window.setCentralWidget (frm)
    # window.resize(240, 120)
    window.show()
    sys.exit(app.exec_())    
    closeConection(dbase)
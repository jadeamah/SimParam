import getopt
import os
import string
import sys
import mysql.connector 
from pyproj import Transformer

from ivy.std_api import *


import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QComboBox, QHBoxLayout, QLabel,QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot


IVYAPPNAME = 'Sim Param'
x = 0
y = 0
airport_select = 0
fligh_plan_send = 0

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Sim Param'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 200
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        hbox = QHBoxLayout()

      
        self.button = QPushButton('Start', self)
        self.button.setToolTip('This button lauch simulation')
        self.button.setEnabled(False)
        self.button.clicked.connect(self.on_click)
        
        self.label = QLineEdit()
        self.label.editingFinished.connect(self.checkAirport)

        

        hbox.addWidget(self.label)
        hbox.setSpacing(20)


        hbox.addWidget(self.button)
        self.setContentsMargins(20, 20, 20, 20)
        self.setLayout(hbox)

        self.move(300, 300)
        
        self.show()
        
    def checkAirport(self, airport):
        global x,y,fligh_plan_send,airport_select
        try:
            #TODO faire la connexion avec la BDD
            mydb = mysql.connector.connect(
              host="localhost",
              user="user_nd",
              password="nd",
              database="jdbc:postgresql://localhost:5432/navDB"
            )

            mycursor = mydb.cursor()
            sql_select_query = """SELECT longitude, latitude from aeroport where identifiant=%s"""
            mycursor.execute(sql_select_query, (airport,))

            myresult = mycursor.fetchall()
            
            trans = Transformer.from_crs(
                "epsg:4326",
                "+proj=utm +zone=10 +ellps=WGS84",
                always_xy=True,
            )
            x, y = trans.transform(myresult[0], myresult[0])
            in_database = 1
            
        except mysql.connector.Error as error:
            print("Failed to get record from MySQL table")
            in_database = 0
        
        if(in_database):
            in_database = 1
            self.label.setStyleSheet("color: green;")
            if(fligh_plan_send & airport_select):
                ex.activeBut()
            print("ok")
        else:
            self.label.setStyleSheet("color: red;")
        
    def activeBut(self):
        self.button.setEnabled(True)
        
    def desactiveBut(self):
        self.button.setEnabled(False)   

    @pyqtSlot()
    def on_click(self):
        global x,y
        msg = "InitStateVector x=" + str(x) +  " y=" + str(y) + " z=500.0 Vp=250.0 fpa=0.0 psi=0.0 phi=0.0"
        IvySendMsg(msg)
        self.desactiveBut()
        print("send")
        
    def closeEvent(self, event):
            close = QMessageBox.question(self,
                                         "QUIT",
                                         "Are you sure want to stop process?",
                                         QMessageBox.Yes | QMessageBox.No)
            if close == QMessageBox.Yes:
                IvyStop()
                event.accept()
            else:
                event.ignore()
            
def leg_list(*arg):
    global fligh_plan_send,airport_select
    fligh_plan_send = 1
    if(fligh_plan_send & airport_select):
        ex.activeBut()
        
            
def lprint(fmt, *arg):
    print(IVYAPPNAME + ': ' + fmt % arg)


def usage(scmd):
    lpathitem = string.split(scmd, '/')
    fmt = '''Usage: %s [-h] [-b IVYBUS | --ivybus=IVYBUS]
    where
    \t-h provides the usage message;
    \t-b IVYBUS | --ivybus=IVYBUS allow to provide the IVYBUS string in the form
    \t adresse:port eg. 127.255.255.255:2010
    '''
    print(fmt % lpathitem[-1])


def oncxproc(agent, connected):
    pass


def ondieproc(agent, _id):
    pass





# initializing ivybus and isreadymsg
sivybus = ''
sisreadymsg = '[%s is ready]' % IVYAPPNAME
# getting option
try:
    optlist, left_args = getopt.getopt(sys.argv[1:], 'hb:', ['ivybus='])
except getopt.GetoptError:
    # print help information and exit:
    usage(sys.argv[0])
    sys.exit(2)
for o, a in optlist:
    if o in ('-h', '--help'):
        usage(sys.argv[0])
        sys.exit()
    elif o in ('-b', '--ivybus'):
        sivybus = a
if sivybus:
    sechoivybus = sivybus
elif 'IVYBUS' in os.environ:
    sechoivybus = os.environ['IVYBUS']
else:
    sechoivybus = 'ivydefault'
lprint('Ivy will broadcast on %s ', sechoivybus)

# initialising the bus
IvyInit(IVYAPPNAME,     # application name for Ivy
        sisreadymsg,    # ready message
        0,              # main loop is local (ie. using IvyMainloop)
        oncxproc,       # handler called on connection/disconnection
        ondieproc)      # handler called when a <die> message is received

# starting the bus
# Note: env variable IVYBUS will be used if no parameter or empty string
IvyBindMsg(leg_list,'^FL_LegList Time=(.*) LegList=(.*)') #FL_LegList Time=100 LegList=50
# is given ; this is performed by IvyStart (C)
IvyStart(sivybus)



app = QApplication(sys.argv)
ex = App()
sys.exit(app.exec_())

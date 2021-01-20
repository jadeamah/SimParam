from PyQt5.QtWidgets import QWidget, QPushButton, QMessageBox, QComboBox, QHBoxLayout, QLabel,QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from ivy.std_api import *
import mysql.connector 
from pyproj import Transformer

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

    def checkAirport(self):
        global x, y, fligh_plan_send, airport_select
        try:
            
            conn = mysql.connector.connect(database="navigationdisplay", 
                        user="user_nd",
                        host="localhost",
                        password="nd") 

            cur = conn.cursor()
            sql_select_query = """SELECT longitude, latitude from aeroport where identifiant=%s"""
            cur.execute(sql_select_query, (self.label.text(),))

            myresult = cur.fetchall()
            conn.close()
            
            print(myresult)
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

        if (in_database):
            in_database = 1
            self.label.setStyleSheet("color: green;")
            if (fligh_plan_send & airport_select):
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
        global x, y
        msg = "InitStateVector x=" + str(x) + " y=" + str(y) + " z=500.0 Vp=250.0 fpa=0.0 psi=0.0 phi=0.0"
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

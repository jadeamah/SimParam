from PyQt5.QtWidgets import QWidget, QPushButton, QMessageBox, QComboBox, QHBoxLayout, QLabel,QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from ivy.std_api import *
import psycopg2 
from pyproj import Transformer


_init_TRAJ_mes =""

# Mercator projection used
trans = Transformer.from_crs("epsg:4326", "+proj=merc +zone=32 +ellps=WGS84 +lat_ts=45", always_xy=True)
NM2M = 1852

x = 0
y = 0
airport_select = 0
traj_team_ready = 0

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
        global x, y, traj_team_ready, airport_select
        id_airport = self.label.text()
        self.conn = psycopg2.connect(database="navdb",
                                user="user_nd",
                                host="localhost",
                                password="nd",
                                port="5432")

        self.cursor = self.conn.cursor()
        self.cursor.execute("""SELECT latitude, longitude  from aeroport where identifiant='{}'""".format(id_airport))
        rows = self.cursor.fetchall()

        self.conn.close()
        
        
        trans = Transformer.from_crs(
            "epsg:4326",
            "+proj=utm +zone=10 +ellps=WGS84",
            always_xy=True,
        )
        
        if rows != []:
            first_wpt = WayPoint(rows[0][0], rows[0][1])
            x, y = first_wpt.x, first_wpt.y
            self.label.setStyleSheet("color: green;")
            airport_select = 1
            msg = "SP_AptId Identifier="+str(id_airport)
            IvySendMsg(msg)
            msg2 = "SP_InitialCoord Lat=" + rows[0][0] + " Lon=" +rows[0][1]
            IvySendMsg(msg2)
            if (traj_team_ready & airport_select):
                self.activeBut()
            
            #Envoi iD airport sur le bus ivy après verif
            
        else:
            self.label.setStyleSheet("color: red;")

    def activeBut(self):
        self.button.setEnabled(True)

    def desactiveBut(self):
        self.button.setEnabled(False)
        
    def get_traj_team_ready(self):
        global traj_team_ready
        return traj_team_ready
        
    def get_airport_select(self):
        global airport_select
        return airport_select
        
    def set_traj_team_ready(self, init_TRAJ_mes):
        global traj_team_ready, _init_TRAJ_mes
        traj_team_ready =1
        _init_TRAJ_mes = init_TRAJ_mes

    @pyqtSlot()
    def on_click(self):
        global x, y, traj_team_ready, airport_select, _init_TRAJ_mes
        msg = "InitStateVector x=" + str(x) + " y=" + str(y) + _init_TRAJ_mes
        IvySendMsg(msg)
        self.desactiveBut()
        airport_select = 0
        traj_team_ready = 0

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

class WayPoint():
    def __init__(self, lat, lon):
        #self.lat, self.lon = lat, lon
        self.lat, self.lon = self.string_to_float(lat, lon)
        self.x, self.y = self.convert()

    def string_to_float(self, lat, lon):
        dir_lat, dir_lon = lat[0], lon[0]
        lat, lon = lat[1:], lon[1:] # the first letter is removed
        lat_float = float(lat[0:2]) + float(lat[2:4]) / 60 + float(lat[4:6]) / 3600
        lon_float = float(lon[0:3]) + float(lon[3:5]) / 60 + float(lon[5:7]) / 3600

        if dir_lat == "S":
            lat = -lat_float
        if dir_lon == "W":
            lon = -lon_float

        return lat_float, lon_float

    def __repr__(self):
        return "({0.x}, {0.y}, {0.lat}, {0.long})".format(self)

    def convert(self):
        y, x = trans.transform(self.lat, self.lon)
        return x/NM2M, y/NM2M

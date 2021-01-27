import getopt
import os
import string
from windowsApp import App
from ivy.std_api import *
from PyQt5.QtWidgets import QApplication

IVYAPPNAME = 'Sim Param'

def change_traj_team_ready(agent, *data):
    init_TRAJ_mes = data[0]
    print("Message d'initialisation de TRAJ :", init_TRAJ_mes)
    ex.set_traj_team_ready()
    
    if(ex.get_airport_select() & ex.get_traj_team_ready()):
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

if __name__ == "__main__":
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


    # wait for TRAJ ready message
    IvyBindMsg(change_traj_team_ready, '^GT Traj_Ready (.*)')

    # is given ; this is performed by IvyStart (C)
    IvyStart(sivybus)

    # Start the application
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

import socketio
import sys
import json
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QObject

form_class = uic.loadUiType("login_window.ui")[0]
form_class2 = uic.loadUiType("main_window.ui")[0]

isLogin = False

class SocketClient(QThread):
    sio = socketio.Client()

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.ip = 'localhost'
        self.port = '8080'
        self.host = 'http://%s:%s' % (self.ip, self.port)

    def run(self):
        SocketClient.sio.connect(self.host)
        SocketClient.sio.on('get_student_login_info', self.get_student_login_info)

    def login(self, id, password, isTeacher):
        SocketClient.sio.emit('login', {
            'id': id,
            'password': password,
            'isTeacher': isTeacher
        })

    def get_student_login_info(self, data):
        self.accessToken = data['data']['accessToken']
        self.classId = data['data']['classId']


class LoginWindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # start socket client
        self.socketClient = SocketClient(self)
        self.socketClient.start()

        # get login info signal
        # self.socketClient.loginInfoSignal.connect(self.getStudentLoginInfo)

        self.id = ''
        self.password = ''
        self.isTeacher = False

        # id line edit
        self.idLineEdit.textChanged.connect(self.idEditChanged)

        # password line edit
        self.passwordLineEdit.textChanged.connect(self.passwordEditChanged)

        # teacher checkbox
        self.teacherCheckBox.stateChanged.connect(self.teacherCheckChanged)

        # button
        self.loginButton.clicked.connect(self.buttonClicked)

    def idEditChanged(self):
        self.id = self.idLineEdit.text()

    def passwordEditChanged(self):
        self.password = self.passwordLineEdit.text()

    def teacherCheckChanged(self):
        self.isTeacher = self.teacherCheckBox.isChecked()

    def buttonClicked(self):
        self.socketClient.login(self.id, self.password, self.isTeacher)
        self.hide()
        self.mainWindow = MainWindowClass()
        self.mainWindow.exec()
        self.show()


class MainWindowClass(QMainWindow, form_class2):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loginWindow = LoginWindowClass()
    loginWindow.setWindowTitle('집ZOOM 클라이언트')
    loginWindow.show()
    app.exec_()

accessToken = None
sio = socketio.Client()

@sio.event
def connect():
    id = input("id를 입력하세요")
    password = input("pw를 입력하세요")
    isTeacher = input("선생님이면 yes 아니면 no")

    if isTeacher == "yes":
        isTeacher = True
    else:
        isTeacher = False

    sio.emit('login', {
        'id': id,
        'password': password,
        'isTeacher':isTeacher
    })

# @sio.event
# def get_teacher_login_info(data):
#     accessToken = data['data']['accessToken']
#     classIdList = data['data']['classId']
#
#     print("현재 선생님 계정에 등록된 반 리스트입니다.")
#     print(classIdList)
#     classId = int(input("반 아이디를 고르세요:"))
#
#     sio.emit('choose_class', {
#         'accessToken': accessToken,
#         'classId': classId
#     })
#
# @sio.event
# def get_student_login_info(data):
#     print(type(data))
#
# @sio.event
# def my_message(data):
#     print('message received with ', data)
#     sio.emit('my response', {'response': 'my response'})
#
#
# @sio.event
# def error(err):
#     print(err)
#
# @sio.event
# def disconnect():
#     print('disconnected from server')
#
# sio.connect('http://localhost:8080')
# sio.wait()
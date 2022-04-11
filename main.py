from cam import run_camera
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import requests
import json

baseURL = "http://3.35.141.211:3000"
form_class = uic.loadUiType("housezoom.ui")[0]

class WindowClass(QMainWindow,form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.loginButton.clicked.connect(self.loginButtonFuntion)

    def loginButtonFuntion(self):
        response = requests.post(baseURL+"/api/login/student", data= {
            "id": self.idTextEdit.toPlainText(),
            "password": self.passwordTextEdit.toPlainText()
        }).json()

        if response['status'] == 'success':
            run_camera()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
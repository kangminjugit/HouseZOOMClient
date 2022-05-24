import eel
import requests
from duringClass import ClassHandle


eel.init('web')


@eel.expose
def login(id, password):
    response = requests.post('http://3.35.141.211:3000/api/login/student', data={
        'id': id,
        'password': password
    })
    response = response.json()
    return response


@eel.expose
def get_timeTable(classId):
    response = requests.get(
        'http://3.35.141.211:3000/api/time-table?classId=%d' % classId)
    response = response.json()
    return response


@eel.expose
def startClass(studentId, classId, accessToken):
    classHandler = ClassHandle(studentId, classId, accessToken)


eel.start('index.html')

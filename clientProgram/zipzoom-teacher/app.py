from asyncio.windows_events import NULL
from email import header
import eel
import requests
import socketio
from pymongo import MongoClient


eel.init('web')

sio = socketio.Client()
# sio.connect('http://3.35.141.211:4040')
sio.connect('http://localhost:4040')


def quizTimeoutHandler(data):
    print(data)


sio.on('quiz_timeout', quizTimeoutHandler)


@eel.expose
def login(id, password):
    response = requests.post('http://3.35.141.211:3000/api/login/teacher', data={
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
def get_studentTable(classId, accessToken):
    headers = {"Authorization": "Bearer %s" % accessToken}
    response = requests.get(
        'http://3.35.141.211:3000/api/student?classId=%d' % classId, headers=headers)
    response = response.json()
    print(response)
    return response


@eel.expose
def startClass(teacherId, accessToken, classId, name):
    print(teacherId, classId)
    sio.emit('teacher_join_class', {
        'data': {
            'teacherId': teacherId,
            'accessToken': accessToken,
            'classId': classId,
            'name': name
        }
    })

    print('join class')


@eel.expose
def givePoint(accessToken, studentId, point, classId):
    sio.emit('give_point', {
        'data': {
            'accessToken': accessToken,
            'studentId': studentId,
            'point': point,
            'classId': classId
        }
    })

    print('give point')


@eel.expose
def giveBadge(accessToken, studentId, point, subject, description, classId):
    sio.emit('give_badge', {
        'data': {
            'accessToken': accessToken,
            'studentId': studentId,
            'point': point,
            'subject': subject,
            'description': description,
            'classId': classId
        }
    })

    print('give badge')


@eel.expose
def giveOXQuiz(classId, teacherID, accessToken, problem, answer, timeLimitMin, timeLimitSec, point, badgeSubject, badgeDescription):
    sio.emit('give_ox_quiz', {
        'data': {
            'classId': classId,
            'teacherId': teacherID,
            'accessToken': accessToken,
            'problem': problem,
            'answer': answer,
            'timeLimitMin': timeLimitMin,
            'timeLimitSec': timeLimitSec,
            'point': point,
            'badgeSubject': badgeSubject,
            'badgeDescription': badgeDescription
        }
    })

    print('give ox quiz')


@eel.expose
def giveChoiceQuiz(classId, teacherID, accessToken, problem, multiChoices, answer, timeLimitMin, timeLimitSec, point, badgeSubject, badgeDescription):
    sio.emit('give_choice_quiz', {
        'data': {
            'classId': classId,
            'teacherId': teacherID,
            'accessToken': accessToken,
            'problem': problem,
            'multiChoices': multiChoices,
            'answer': answer,
            'timeLimitMin': timeLimitMin,
            'timeLimitSec': timeLimitSec,
            'point': point,
            'badgeSubject': badgeSubject,
            'badgeDescription': badgeDescription
        }
    })

    print('give choice quiz')


@eel.expose
def get_classList(accessToken):
    headers = {"Authorization": "Bearer %s" % accessToken}
    response = requests.get(
        'http://3.35.141.211:3000/api/class/my-class', headers=headers)
    return response.json()


@eel.expose
def get_quizResult(classId):
    mongo = MongoClient(
        'mongodb://ec2-3-38-116-33.ap-northeast-2.compute.amazonaws.com', 27017)
    print(mongo)

    filter = {'classId': classId}
    result = mongo['housezoom']['room'].find_one(filter)

    if result:
        studentAnswerArr = result['studentAnswerArr']
        quizArr = result['quizArr']

        # print(result)
        return (quizArr, studentAnswerArr)
    else:
        return NULL


eel.start('index.html', port=8090)

// var createError = require('http-errors');
const app = require('express')();
const server = require('http').createServer(app);
const PORT = 4040;
const io = require('socket.io')(server);
const axios = require('axios');
const { access } = require('fs');
const jwt = require('jsonwebtoken');
const { type } = require('os');
const internal = require('stream');
const http = require('./api');
const {addUser} = require('./user');

// var path = require('path');
// var cookieParser = require('cookie-parser');
// var logger = require('morgan');

// var indexRouter = require('./routes/index');
// var usersRouter = require('./routes/users');

var studentSockets = {};
var teacherSockets = {};

var quiz = {};
var studentAnswers = {};

var classes = {};

function quizTimeoutFunction(socket, classId, answer){
  var studentAnswerArr = [];
  classes[classId].forEach(studentId => {
    if(studentSockets[studentId]){
      studentSockets[studentId].emit('quiz_timeout', {
        'data':{
          'message': '퀴즈가 종료되었습니다!',
          'is_ox': quiz[classId]['is_ox'],
          'answer': answer,
          'studentAnswer': studentAnswers[studentId],
          'is_correct': answer === studentAnswers[studentId] ? true: false,
        }
      });

      if(answer === studentAnswers[studentId]){
        // api로 db 업데이트
        axios.post('http://3.35.141.211:3000/api/point',{
          'is_ox': quiz[classId]['is_ox'],
          'studentId' : studentId,
          'point':quiz[classId]['point']        
        },{
          headers: { Authorization: `Bearer ${quiz[classId]['accessToken']}` },
        } );

        // // api로 db 업데이트
        // axios.post('http://3.35.141.211:3000/api/badge',{
        //   'studentId' : studentId,
        //   'point':point,
        //   'subject': subject,
        //   'description': '퀴즈 '
        // },{
        //   headers: { Authorization: `Bearer ${accessToken}` },
        // } ).then(res => {
          
        // });
      }

      studentAnswerArr.push({
        'studentId': studentId,
        'studentAnswer': studentAnswers[studentId] 
      });
    }
  });

  teacherSockets[quiz[classId]['teacherId']].emit('quiz_timeout', {
    'data': {
      'message': '퀴즈가 종료되었습니다!',
      'studentAnswerArr': studentAnswerArr
    }
  });
}

io.on('connection', (socket) => {
  var newQuizId = 0;
  
  // 로그인 요청 처리
  socket.on('login', async (data, callback) => {
    // const {classId} = data;
    // socket.join(classId);
    // console.log('login request');
    const {id, password, isTeacher} = data;
    const {accessToken, classId, error} = await addUser(socket.id, id, password, isTeacher);
    
    // 로그인 중 에러 처리
    if(error) {
      console.log(error);
      socket.emit('error', {
        message: error.message
      });
      return;
    }

    // 선생님 유저인 경우 access token과 등록된 반 리스트 전송
    if(isTeacher){
      socket.emit('get_teacher_login_info', {
        data: {
          accessToken: accessToken,
          classId: classId
        }
      });
    }
    // 학생 유저인 경우 해당 반아이디 room에 접속 ,access token과 등록된 반 전송 
    else{
      socket.join(classId);
      socket.emit('get_student_login_info', {
        data: {
          accessToken: accessToken,
          classId: classId
        }
      });
    }
  })

  socket.on('choose_class', async(data, callback) => {
    const {data: {accessToken, classId}} = data;
    socket.join(classId);
  });

  // socket.on('createQuiz', message => {
  //   // 퀴즈 타입(객관식 or OX), 문제, 선지, 답과 함께 퀴즈 생성
  //   const {type, quiz, elems, answer} = message;

  // })

  socket.on('student_join_class',async(data, callback) => {
    const {data: {studentId, classId}} = data;
    socket.join(classId);
    studentSockets[studentId] = socket;

    console.log(studentId+' joined');

    // 접속한 학생 저장
    if(!classes[classId]){
      classes[classId] = [];
    }
    classes[classId].push(studentId);
  });

  socket.on('teacher_join_class',async(data, callback) => {
    const {data: {teacherId, classId}} = data;
    socket.join(classId);
    teacherSockets[teacherId] = socket;

    console.log(teacherId+' joined');
    // 접속한 학생 저장
    if(!classes[classId]){
      classes[classId] = [];
    }
    classes[classId].push(teacherId);
  });

  socket.on('give_point', async(data, callback) => {
    const {data: {accessToken, classId, studentId, point}} = data;

    // api로 db 업데이트
    axios.post('http://3.35.141.211:3000/api/point',{
      'studentId' : studentId,
      'point':point        
    },{
      headers: { Authorization: `Bearer ${accessToken}` },
    } ).then(res => {
      
    });

    // 학생 소켓 찾기
    var studentSocket = studentSockets[studentId];

    // 학생 소켓에 알리기
    if(studentSocket){
      studentSocket.emit('get_point', {
        'data':{
          'studentId': studentId,
          'point': point
        }
      });
    }
  })

  socket.on('give_badge', async(data, callback) => {
    const {data: {accessToken, studentId, point, subject, description}} = data;

    // api로 db 업데이트
    axios.post('http://3.35.141.211:3000/api/badge',{
      'studentId' : studentId,
      'point':point,
      'subject': subject,
      'description': description
    },{
      headers: { Authorization: `Bearer ${accessToken}` },
    } ).then(res => {
      
    });

    // 학생 소켓 찾기
    var studentSocket = studentSockets[studentId];

    // 학생 소켓에 알리기
    if(studentSocket){
      studentSocket.emit('get_badge', {
        'data':{
          'studentId' : studentId,
          'point':point,
          'subject': subject,
          'description': description
        }
      });
    }
  })

  socket.on('give_ox_quiz', (data, callback) => {
    const {data: {classId,teacherId,accessToken, problem, answer, timeLimitMin, timeLimitSec, point}} = data;

    quiz[classId] = {
      'is_ox': true,
      'problem': problem, 
      'answer': answer === 'O' ? 1 : 2,
      'point': point ,
      'teacherId':teacherId,
      'accessToken':accessToken
    };

    socket.to(classId).emit('get_ox_quiz', {
      'data':{
        'problem': problem,
        'point':point,
        'timeLimitMin': timeLimitMin,
        'timeLimitSec': timeLimitSec
      }
    });

    setTimeout(quizTimeoutFunction, 1000*timeLimitSec+1000*60*timeLimitMin,socket, classId, answer === 'O' ? 1 : 2);
  })


  socket.on('give_choice_quiz', (data, callback) => {
    const {data: {classId,teacherId,accessToken, problem, multiChoices, answer, timeLimitMin, timeLimitSec, point, badge}} = data;
    quiz[classId] = {
      'is_ox': false,
      'problem': problem, 
      'answer': parseInt(answer),
      'point': point ,
      'teacherId':teacherId,
      'accessToken':accessToken,
      'badge': badge
    };

    socket.to(classId).emit('get_choice_quiz', {
      'data':{
        'problem': problem,
        'multiChoices':multiChoices,
        'point':point,
        'timeLimitMin': timeLimitMin,
        'timeLimitSec': timeLimitSec
      }
    });

    setTimeout(quizTimeoutFunction, 1000*timeLimitSec+1000*60*timeLimitMin,socket, classId, parseInt(answer));
  });

  socket.on('submit_quiz', (data, callback) => {
    const {data: {classId, studentId, answer}} = data;
    studentAnswers[studentId] = answer;
  });
  
  socket.on('disconnect', () => {
  
  })
});

app.get('/', (req, res) => {
  res.send('socket server is running');
})

server.listen(PORT, () => {
  console.log('listening on http://localhost:4040/');
})

// // view engine setup
// app.set('views', path.join(__dirname, 'views'));
// app.set('view engine', 'jade');

// app.use(logger('dev'));
// app.use(express.json());
// app.use(express.urlencoded({ extended: false }));
// app.use(cookieParser());
// app.use(express.static(path.join(__dirname, 'public')));

// app.use('/', indexRouter);
// app.use('/users', usersRouter);

// // catch 404 and forward to error handler
// app.use(function(req, res, next) {
//   next(createError(404));
// });

// // error handler
// app.use(function(err, req, res, next) {
//   // set locals, only providing error in development
//   res.locals.message = err.message;
//   res.locals.error = req.app.get('env') === 'development' ? err : {};

//   // render the error page
//   res.status(err.status || 500);
//   res.render('error');
// });

module.exports = app;

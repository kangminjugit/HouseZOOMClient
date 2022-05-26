document.getElementById('submitBtn').addEventListener('click', () => {
    var classId = JSON.parse(localStorage.getItem('classId'));
    var teacherID = JSON.parse(localStorage.getItem('teacherID'));
    var accessToken = JSON.parse(localStorage.getItem('accessToken'));
    var problem = document.getElementById('quiz').value;
    var answer = document.getElementById('gridRadios1').checked;
    var timeLimitMin = document.getElementById('time-limit-min').value;
    var timeLimitSec = document.getElementById('time-limit-sec').value;
    var point = document.getElementById('point').value;

    eel.giveOXQuiz(classId,teacherID,accessToken, problem, answer, timeLimitMin, timeLimitSec, point);
  });
  
var choiceCnt = 2;
function addChoice(){
    choiceCnt++;
    console.log('add choice');
    var multipleChoiceInputs = document.getElementById('multiple-choice-foreword');

    const html = `
    <div class="input-group mb-3">
    <input type="text" class="form-control multiple-choice-content" placeholder="${choiceCnt}번 객관식 선지 내용">
    <div class="input-group-append">
      <button class="btn btn-outline-danger add-choice-btn" type="button">삭제</button>
    </div>
    </div>`;
    const template = document.createElement('div');
    template.innerHTML = html;
    console.log(multipleChoiceInputs.appendChild(template));


    var answerSelect = document.getElementById('answer');

    const option = `${choiceCnt}`;
    const template2 = document.createElement('option');
    template2.innerHTML = option;
    template2.value = `${choiceCnt}`;
    answerSelect.appendChild(template2);
}

document.getElementById('submitBtn').addEventListener('click', () => {
  var classId = JSON.parse(localStorage.getItem('classId'));
  var teacherId = JSON.parse(localStorage.getItem('teacherID'));
  var accessToken = JSON.parse(localStorage.getItem('accessToken'));

  var problem = document.getElementById('quiz').value;
  var multiChoices = []; 
  var multiChoicesDoc = document.getElementsByClassName('multiple-choice-content');
  for(var i=0; i<multiChoicesDoc.length; i++){
    multiChoices.push(multiChoicesDoc[i].value);
  }

  var answerElem = document.getElementById('answer');
  var answer = answerElem.options[answerElem.selectedIndex].value;

  var timeLimitMin = document.getElementById('time-limit-min').value;
  var timeLimitSec = document.getElementById('time-limit-sec').value;
  var point = document.getElementById('point').value;
  // var badge = document.getElementById('badge').value;

  // console.log(classId, problem, multiChoices, answer, timeLimitMin, timeLimitSec, point);
  // eel.giveChoiceQuiz(classId,teacherId,accessToken, problem, multiChoices, answer, timeLimitMin, timeLimitSec, point, badge);
  eel.giveChoiceQuiz(classId,teacherId,accessToken, problem, multiChoices, answer, timeLimitMin, timeLimitSec, point);
});

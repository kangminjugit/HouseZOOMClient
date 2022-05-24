document.getElementById('compliment_point_btn').addEventListener('click', () => {
    var accessToken = JSON.parse(localStorage.getItem('accessToken'));
    var classId = JSON.parse(localStorage.getItem('classId'));
	var studentId = document.getElementById('compliment_point_input').value;
    var point = document.getElementById('compliment_point_input2').value;
    eel.givePoint(accessToken, studentId, point);
});
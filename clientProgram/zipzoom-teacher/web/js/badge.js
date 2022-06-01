document.getElementById('badge_btn').addEventListener('click', () => {
    var accessToken = JSON.parse(localStorage.getItem('accessToken'));
	var studentId = document.getElementById('badge_input').value;
    var point = document.getElementById('badge_input2').value;
    var subject = document.getElementById('badge_input3').value;
    var description = document.getElementById('badge_input4').value;

    eel.giveBadge(accessToken, studentId, point, subject, description);
});
async function login(id, password){
	var response = await eel.login(id, password)();
    localStorage.setItem('teacherID', JSON.stringify(id));
	localStorage.setItem('accessToken',JSON.stringify(response['data']['accessToken']));
	localStorage.setItem('classId',JSON.stringify(response['data']['classId'][0]));

	window.location.href = "main.html";
}

document.getElementById('btn_login').addEventListener('click', () => {
	var id = document.getElementById('id').value;
	var password = document.getElementById('password').value;
	login(id, password);
    eel.startClass(JSON.parse(localStorage.getItem('teacherID')), JSON.parse(localStorage.getItem('classId')));
});
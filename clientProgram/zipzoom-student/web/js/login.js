async function login(id, password){
	var response = await eel.login(id, password)();
	localStorage.setItem('studentId',JSON.stringify(id));
	localStorage.setItem('accessToken',JSON.stringify(response['data']['accessToken']));
	localStorage.setItem('classId',JSON.stringify(response['data']['classId']));
	
	window.location.href = "main.html";
}

document.getElementById('btn_login').addEventListener('click', () => {
	console.log('login button clicked');
	var id = document.getElementById('id').value;
	var password = document.getElementById('password').value;
	login(id, password);
});
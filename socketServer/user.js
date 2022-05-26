const http = require('./api');

const addUser = async (socketId, userId, userPassword, isTeacher) => {
    try{
        if(!userId || !userPassword){
            const error = {
                status: 'error',
                code: 400,
                data:null,
                message: '아이디, 패스워드가 필요합니다.'
            };
            return {error};
        }
        
        let response = null;
        if(isTeacher){
            response = await http.post('/api/login/teacher', {
                id: userId,
                password: userPassword
            });
        }else{
            response = await http.post('/api/login/student', {
                id: userId,
                password: userPassword
            });
        }

        const accessToken = response.data.data.accessToken;
        const classId = response.data.data.classId;

        return {accessToken, classId};
    }catch(error){
        error = error.response.data;
        return {error};
    }
}

module.exports = {addUser};
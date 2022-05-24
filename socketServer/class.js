const http = require('./api');

const getClassInfo = async (classId) => {
    try{
        if(!classId){
            const error = {
                status: 'error',
                code: 400,
                data:null,
                message: '반 아이디가 필요합니다.'
            };
            return {error};
        }
        
        const response = await http.post('/api/login/teacher', {
            id: userId,
            password: userPassword
        });

        const classId = response.data.data.classId;

        return {accessToken, classId};
    }catch(error){
        error = error.response.data;
        return {error};
    }
}

module.exports = {getClassInfo};
const axios = require('axios');

const http = axios.create({
    baseURL: 'http://3.35.141.211:3000'
});

module.exports = http;
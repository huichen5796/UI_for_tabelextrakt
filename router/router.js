const express = require('express');
const router = express.Router();
const router_handler = require('../router_handler/router_handler.js') 

router.post('/run', router_handler.inputData)

module.exports = router;

const express = require('express');
const router = express.Router();
const router_handler = require('../router_handler/router_handler.js') 

router.get('/responseData', router_handler.forAjax)

router.post('/run', router_handler.runPy)

router.post('/return', router_handler.returnTable)

router.post('/returnSearch', router_handler.returnSearch)

router.post('/searchLabel', router_handler.searchLabel)

module.exports = router;

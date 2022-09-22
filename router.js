const express = require('express');
const router = express.Router();
const router_handler = require('./router_handler.js') 

router.post('/upload', router_handler.upload)

router.post('/run', router_handler.runPy)

router.post('/return', router_handler.returnTable)

router.post('/returnSearch', router_handler.returnSearch)

router.post('/searchLabel', router_handler.searchLabel)

router.post('/imageOriShow', router_handler.imageOriSchow)

module.exports = router;

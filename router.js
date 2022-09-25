const express = require('express');
const router = express.Router();
const router_handler = require('./router_handler.js') 

router.post('/upload', router_handler.upload)

router.post('/run', router_handler.runPy)

router.post('/returnSearch', router_handler.returnSearch)

router.post('/searchLabel', router_handler.searchLabel)

router.post('/seeResult', router_handler.seeResult)

router.post('/clean', router_handler.cleanAll)

router.post('/continue', router_handler.continue)

module.exports = router;

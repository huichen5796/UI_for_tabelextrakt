const express = require('express');
const router = express.Router();
const router_handler = require('./router_handler.js')

router.post('/upload', router_handler.upload)

router.post('/uploadStapel', router_handler.uploadStapel)

router.post('/run', router_handler.runPy)

router.post('/search', router_handler.search) // returns the table information found in elasticsearch

router.post('/searchLabel', router_handler.searchLabel)

router.post('/seeDetail', router_handler.seeDetail)

router.post('/clean', router_handler.cleanAll)

router.post('/continue', router_handler.continue)

router.post('/saveExcel', router_handler.saveExcel)

router.post('/getProgress', router_handler.getProgress)

router.post('/continueRun', router_handler.continueRun)

module.exports = router;

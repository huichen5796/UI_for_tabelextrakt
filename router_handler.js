const spawn = require('child_process').spawn
const formidable = require('formidable')
const path = require('path')

exports.uploadStapel = (req, res) => {
    const form = new formidable.IncomingForm()
    form.uploadDir = path.join(__dirname, 'assets', 'uploads')

    form.keepExtenSions = true
    let arr = []

    form.on('file', (name, file) => {
        arr.push({
            todo: 'uploadStapel',
            path: file.filepath.split('assets')[1],
            fileName: file.originalFilename
        })
    })

    form.parse(req, (err, fields, files) => {
        var imagesPath = {
            todo: 'uploadStapel',
            data: arr
        }
        console.log({
            todo: 'uploadStapel',
            data: 'see details in arr'
        })

        const imagesPathStr = JSON.stringify(imagesPath)
        // console.log(imagesPathStr)
        const py = spawn('python', ['main.py', imagesPathStr])

        /* Output the print content in the py file */
        py.stdout.on('data', function (result) {
            const data = JSON.parse(result.toString())
            // console.log(data)
            if (data.massage === 'success') {
                // console.log(data)
                res.send(data)

                console.log('success ' + "todo: 'uploadStapel'")
            } else {
                console.log('error ' + "todo: 'uploadStapel'")
            }
        })

    })
}

exports.upload = (req, res) => {
    const form = new formidable.IncomingForm()
    form.uploadDir = path.join(__dirname, 'assets', 'uploads')

    form.keepExtenSions = true
    form.parse(req, (err, fields, files) => {
        var imagePath = {
            todo: 'upload',
            path: files.attrName.filepath.split('assets')[1],
            // fileBinarName: files.attrName.filepath.split("uploads\\")[1],
            fileName: files.attrName.originalFilename
        }
        console.log(imagePath)

        const imagePathStr = JSON.stringify(imagePath)

        const py = spawn('python', ['main.py', imagePathStr])

        /* Output the print content in the py file */
        py.stdout.on('data', function (result) {
            const data = JSON.parse(result.toString())
            // console.log(data)
            if (data.massage === 'success') {
                // console.log(data)
                res.send(data)

                console.log('success ' + "todo: 'upload'")
            } else {
                console.log('error ' + "todo: 'upload'")
            }
        })


    })
}

exports.runPy = (req, res) => {
    const body = req.body
    const run = {
        todo: 'run',
        model: body.model,
    }
    console.log(run)
    const runStr = JSON.stringify(run)
    const py = spawn('python', ['main.py', runStr])

    /* Output the print content in the py file */
    py.stdout.on('data', function (result) {
        const data = JSON.parse(result.toString())
        if (data.massage === 'success') {
            // console.log(data)
            res.send(data)
            console.log('success ' + "todo: 'run'")
        }
        else {
            res.send(data)
            console.log('error ' + "todo: 'run'")
        }

    })
}

exports.search = (req, res) => {
    const body = req.body
    const search = {
        'todo': 'search',
        'idx': body.idx,
        'label': body.label
    }
    console.log(search)
    const searchJSON = JSON.stringify(search)
    const py = spawn('python', ['main.py', searchJSON])

    /* Output the print content in the py file */
    py.stdout.on('data', function (resultSearch) {
        const data = JSON.parse(resultSearch.toString())
        // console.log(data)
        if (data.massage === 'error') {
            res.send(data)
            console.log('error ' + "todo: 'search'")
        } else {
            // console.log(data)
            res.send(data)
            console.log('success ' + "todo: 'search'")
        }

    })
}

exports.searchLabel = (req, res) => {
    const body = req.body
    const search = {
        'todo': 'searchLabel',
        'idx': body.idx,
        'label': body.label //actually is here 'all'
    }
    console.log(search)
    const searchJSON = JSON.stringify(search)
    const py = spawn('python', ['main.py', searchJSON])

    /* Output the print content in the py file */
    py.stdout.on('data', function (resultSearch) {
        const data = resultSearch.toString()
        // console.log(data)
        if (data === '["error"]') {
            res.send(data)
            console.log('error ' + "todo: 'searchLabel'")
        } else {
            // console.log('Add labels ' + data)
            res.send(data)
            console.log('success ' + "todo: 'searchLabel'")
        }
    })
}

exports.seeDetail = (req, res) => {
    const body = req.body
    const search = {
        'todo': 'seeDetail',
        'image': body.image,
    }
    console.log(search)
    const searchStr = JSON.stringify(search)
    const py = spawn('python', ['main.py', searchStr])

    /* Output the print content in the py file */
    py.stdout.on('data', function (result) {
        const data = JSON.parse(result.toString())
        // console.log(data.massage)
        if (data.massage == 'success') {
            res.send(data)
            console.log('success ' + "todo: 'seeDetail'")
        } else {
            res.send(data)
            console.log('error ' + "todo: 'seeDetail'")
        }

    })
}

exports.cleanAll = (req, res) => {
    const body = req.body
    const clean = {
        'todo': body.todo,
    }
    console.log(clean)
    const cleanStr = JSON.stringify(clean)
    const py = spawn('python', ['main.py', cleanStr])

    /* Output the print content in the py file */
    py.stdout.on('data', function (result) {
        const data = JSON.parse(result.toString())
        // console.log(data)
        if (data.massage == 'success') {
            res.send(data)
            console.log('success ' + "todo: " + body.todo)
        } else {
            res.send(data)
            console.log('error ' + "todo: " + body.todo)
        }

    })
}

exports.continue = (req, res) => {
    const body = req.body
    const cont = {
        'todo': body.todo,
    }
    console.log(cont)
    const contStr = JSON.stringify(cont)
    const py = spawn('python', ['main.py', contStr])

    /* Output the print content in the py file */
    py.stdout.on('data', function (result) {
        const data = JSON.parse(result.toString())
        // console.log(data)
        if (data.massage == 'success') {
            res.send(data)
            console.log('success ' + "todo: " + body.todo)
        } else {
            res.send(data)
            console.log('error ' + "todo: " + body.todo)
        }

    })
}

exports.saveExcel = (req, res) => {
    const body = req.body
    const saveEx = {
        'todo': body.todo,
        'tableId': body.tableId,
    }
    console.log(saveEx)
    const saveExStr = JSON.stringify(saveEx)
    const py = spawn('python', ['main.py', saveExStr])

    /* Output the print content in the py file */
    py.stdout.on('data', function (result) {
        const data = JSON.parse(result.toString())
        // console.log(data)
        if (data.massage == 'success') {
            res.send(data)
            console.log('success ' + "todo: " + body.todo)
        } else {
            res.send(data)
            console.log('error ' + "todo: " + body.todo)
        }

    })
}

exports.getProgress = (req, res) => {
    const body = req.body
    const getP = {
        'todo': body.todo,
    }
    console.log(getP)
    const getPStr = JSON.stringify(getP)
    const py = spawn('python', ['main.py', getPStr])

    /* Output the print content in the py file */
    py.stdout.on('data', function (result) {
        const data = JSON.parse(result.toString())
        // console.log(data)
        if (data.massage == 'success') {
            res.send(data)
            console.log('success ' + "todo: " + body.todo)
        } else {
            res.send(data)
            console.log('error ' + "todo: " + body.todo)
        }

    })
}

exports.continueRun = (req,res)=>{
    const body = req.body
    const conRun = {
        todo: body.todo,
    }
    console.log(conRun)
    const conRunStr = JSON.stringify(conRun)
    const py = spawn('python', ['main.py', conRunStr])

    /* Output the print content in the py file */
    py.stdout.on('data', function (result) {
        const data = JSON.parse(result.toString())
        if (data.massage === 'success') {
            // console.log(data)
            res.send(data)
            console.log('success ' + "todo: 'continueRun'")
        }
        else {
            res.send(data)
            console.log('error ' + "todo: 'continueRun'")
        }

    })
}
const spawn = require('child_process').spawn

exports.forAjax = (req, res) => {
    res.send({ 'name': 'das' })
}

exports.runPy = (req, res) => {
    const body = req.body
    if (body.model && body.file) {

        const run = {
            'todo': 'run',
            'file': body.file,
            'model': body.model
        }
        console.log(run)
        const runJSON = JSON.stringify(run)
        const py = spawn('python', ['main.py', runJSON])

        /* Output the print content in the py file */
        let output = "";
        py.stdout.on("data", (data) => {
            output += data.toString();
        });
        py.on("close", () => {
            console.log(output);
        });

    }
    else {
        if (!body.model & body.file) {
            console.log('No model selected')
        }
        if (!body.file && body.model) {
            console.log('No file selected')
        }
        if (!body.model && !body.file) {
            console.log('Please upload files and select a model to use')
        }

    }
}


exports.returnTable = (req, res) => {
    console.log(res.body)
}

exports.returnSearch = (req, res) => {
    const body = req.body
    if (body.label != '--none--') {

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
            console.log(data)
            res.send(data)
        })
    }
    else {

        console.log('No label selected')


    }
}

exports.searchLabel = (req, res) => {
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
        const data = resultSearch.toString()
        console.log(data)
        res.send(data)
    })
}
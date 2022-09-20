
const spawn = require('child_process').spawn


exports.runPy = (req, res) => {
    const body = req.body
    if (body.model&&body.file) {
        console.log('model to use: ' + body.model)
        const run = {
            'file':body.file,
            'model':body.model
        }
        const runJSON = JSON.stringify(run)
        const py = spawn('python', ['main.py', runJSON])

        /* Output the print content in the py file */
        let output="";
        py.stdout.on("data", (data) => {
            output += data.toString();
        });
        py.on("close", () => {
            console.log(output);
        });
        
    }
    else {
        if (!body.model&body.file){
            console.log('No model selected')
        }
        if (!body.file&&body.model) {
            console.log('No file selected')
        }
        if (!body.model&&!body.file){
            console.log('Please upload files and select a model to use')
        }
        
    }
}

exports.outTable = (req, res) => {
    const py = spawn('python', ['main.py'])
}
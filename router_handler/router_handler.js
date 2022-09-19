const spawn = require('child_process').spawn


exports.runPy = (req, res) => {
    const body = req.body
    if (body.model) {
        console.log('model to use: ' + body.model)

        const py = spawn('python', ['main.py', body.model])

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
        console.log('No model selected')
    }
}

exports.outTable = (req, res) => {
    const py = spawn('python', ['main.py'])
}
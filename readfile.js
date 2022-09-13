const fs = require('fs');

function readFile(filePath) {

    return new Promise((resolve, reject) => {
        fs.readFile(filePath, 'utf-8', (error, ss) => {

            if (error) {
                reject(error);
            }
            else {
                resolve(ss);
            }
        });
    });
}
module.exports = readFile;

// Get read failure and success results -- error, con
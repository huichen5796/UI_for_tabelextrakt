const http = require('http');    /*ähnlich wie import in Python*/
const hostname = '127.0.0.1'
const port = 3000;
const path = require('path');
const url = require('url');

const read_file = require('./readfile.js');
const static_path = file => path.join('D:\\batch_drawing', file);
/* 
'=>' ist gleich wie function(file){... return file;} 
if zwei parameter: (a,b) => a+b ist gleich wie function(a,b){return a+b;}
*/

/* 'let' ist nur günstig in '{}' */
const server = http.createServer((req, res) => {
  let ourl = url.parse(req.url);
  let path_name = ourl.pathname;
  if (path_name == '/favicon.ico') {
    res.end('');
    return;
  }

  path_name = path_name === '/' ? 'web.html' : path_name;

  /* '===' if true do '?' else do ':' */

  let ext_name = path.extname(path_name);
  if (ext_name) {
    read_file(static_path(path_name))
      .then(ss => {
        res.end(ss);
      })
      .catch(error => {
        res.end(JSON.stringify(error));
      });
  }
});

server.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);
});
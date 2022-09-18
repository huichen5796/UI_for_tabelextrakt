const express = require('express');    /*ähnlich wie import in Python*/
const hostname = '127.0.0.1'
const port = 3000;
const router = require('./router/router.js')
const path = require('path');
const url = require('url');
const read_file = require('./assets/readfile.js');

const app = express();

/* Erstellen einen statischen Ressourcenserver */
app.use(express.static('assets'));
app.use(express.json());
app.use(express.urlencoded({extended: false}));

app.use(router)

/* Generieren eine anfängliche statische Seite */
app.get('/', (req, res) => {
  res.sendFile( "D:/batch_drawing/assets/web.html");
});

app.use(function (err, req, res, next) {
  res.send('ERROR in Server!!<br>' + err.message);
});

app.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);
});
const express = require('express');    /*ähnlich wie import in Python*/
const path = require('path')
const hostname = '127.0.0.1'
const port = 4200;
const router = require('./router.js')
const cors = require('cors')

const app = express();

app.use(cors())
/* Erstellen einen statischen Ressourcenserver */
app.use(express.static('assets'));
app.use(express.json());
app.use(express.urlencoded({extended: false}));

app.use(router)

/* Generieren eine anfängliche statische Seite */
app.get('/', (req, res) => {
  
  res.sendFile(path.join(__dirname, 'assets', 'web.html'));
});

app.use(function (err, req, res, next) {
  res.send('ERROR in Server!!<br>' + err.message);
});

app.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);
});
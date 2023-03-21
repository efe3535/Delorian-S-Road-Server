var express = require('express');  
var app = express();  
var bodyParser = require('body-parser');  
var urlencodedParser = bodyParser.urlencoded({ extended: false })  
var fs = require("fs")
app.use(express.static('public'));  
app.use(express.json());
app.post('/register', urlencodedParser, function (req, res) {  
	let file = JSON.parse(fs.readFileSync("./users.json", "utf-8"));
	console.log(req.body);
	file.users.push({username:req.body.username, pass:req.body.pass});
	fs.writeFileSync("./users.json",JSON.stringify(file));
   res.send(JSON.stringify({status:"success"}));  
})

app.post('/login', urlencodedParser, function (req, res) {  
	let file = JSON.parse(fs.readFileSync("./users.json", "utf-8"));
   	let filterFile = file.users.filter(item=>(item.username==req.body.username && item.pass == req.body.pass))
	console.log(req.body)
	if(filterFile.length>0) {
		console.log("login success")
		res.send({status:"success"});  
	} else {
		console.log("login fail")
		res.send({status:"fail"});
	}
})

var server = app.listen(3366, function () {  
})  

#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import re
from google.appengine.ext import ndb
from webapp2_extras import sessions
import session_module

class User(ndb.Model):
    nombre = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    created= ndb.DateTimeProperty(auto_now_add=True)

MAIN_PAGE_HTML = """\
    <html>
    <head>
    <link rel='stylesheet' href='stylesheets/main.css'>
        <script src='scripts/jquery-1.11.3.min.js'></script>
        <script>
            function validar() {
                var nombreBien = true;
                var passwordBien = true;
                var passwordCoinciden = true;
                var emailBien = true;
                document.getElementById('errorName').innerText = "";
                document.getElementById('errorPassword').innerText = "";
                document.getElementById('errorRepetir').innerText = "";
                document.getElementById('errorEmail').innerHTML = "";
                document.getElementById('nombreSaludo').innerHTML = "";

                if(document.getElementById('name').value == "") {
                    document.getElementById('errorName').innerText = "Usuario vacio";
                    nombreBien = false;
                }

                if(document.getElementById('password').value == "") {
                    document.getElementById('errorPassword').innerText = "Password vacia";
                    passwordBien = false;
                }
                                
                if(document.getElementById('password').value != document.getElementById('repeatPassword').value) {
                    document.getElementById('errorRepetir').innerText = "Los password no coinciden";
                    passwordCoinciden = false;
                }

                expr = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
                if ( !expr.test(document.getElementById('email').value) ) {
                    document.getElementById('errorEmail').innerText = "Email vacio o incorrecto";
                    emailBien = false;
                }

                if(nombreBien && passwordBien && passwordCoinciden && emailBien) {
                    document.getElementById('nombreSaludo').innerHTML = "<p >Kaixo: " + document.getElementById('name').value + "<p><p>Tus datos son correctos</p>";
                }
            }
            
            function validarEmail(){
                $("#errorEmail").html('Procesando...');
                email = $("#email").val();
                $.ajax("/comprobar",
                        { 
                            "type": "post",
                            "data":{email:email},
                            "success": function(result) {
                                if(result == 'success'){
                                    $("#errorEmail").html("Email sin usar");
                                } else {
                                    $("#errorEmail").html("Email utilizado");
                                }
                            },

                            "async": true,
                        }
                )
        }
        </script>
    </head>
      <body>
        <h1 id="titulo">DSSW-Tarea 2</h1>
        <h2>Rellene los campos por favor:</h2>
        <form method="post" action="/validar">
            <label class="etiquetas">Nombre: </label>
            <input id="name" name="nombre" type="text" />
            <label id="errorName"></label><br><br>
            <label class="etiquetas">Password: </label>
            <input id="password" name="password" type="password" />
            <label id="errorPassword"></label><br><br>
            <label class="etiquetas">Repeat password: </label>
            <input id="repeatPassword" name="repeatPassword" type="password" /> 
            <label id="errorRepetir"></label><br><br>
            <label class="etiquetas">Email: </label>
            <input id="email" name="email" onChange="validarEmail()" type="email" />
            <label id="errorEmail"></label><br><br>
            <input id="Validar" name="Validar" type="button" onClick="validar()" value="Validar" />
            <input type="submit" value="Enviar a servidor" />
        </form>
        <div id="nombreSaludo"></div>
        </body>
    </html>
"""

FORM_LOGIN="""
<html>
    <body>
        <form action="/comprobarLogin" method="POST">
            <label class="etiquetas">Email: </label>
            <input id="email" name="email" type="email" />
            <label id="errorEmail"></label><br><br>
            <label class="etiquetas">Password: </label>
            <input id="password" name="password" type="password" />
            <label id="errorPassword"></label><br><br>
            <input type="submit" value="Entrar" />
        </form>
    </body>
</html>"""

FORM_SUBIR_FOTO="""
<html>
    <body>
        <form action="%(url)s" method="POST" enctype="multipart/form-data">
            <input type="file" name="file"><br>
            <input type="radio" name="access" value="public" checked="checked" />    Public
            <input type="radio" name="access" value="private" /> Private<p>
            <input type="submit" name="submit" value="Submit">
        </form>
    </body>
</html>"""

class Inicio(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("<head>"
        							"<link rel='stylesheet' href='stylesheets/main.css'>"
        						"</head>"
        						"<body>"
        							"<h1>Pagina inicial DSSW</h1>"
        							"<h2>Elige tu saludo (Tarea 1)</h2>"
        							"<a href='/kaixo'>Euskara</a><br>"
        							"<a href='/hola'>Castellano</a><br>"
        							"<a href='/hello'>Ingles</a><br><br>"
                                    "<h2>O registrate si quieres (Tarea 2)</h2>"
                                    "<a href='/registro'>Registro</a><br>"
                                    "<a href='/login'>Login</a><br><br>"
        							"<img src='images/python.jpg' height='200' width='200'>"
								"</body>")

class Euskara(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("<head>"
        							"<link rel='stylesheet' href='stylesheets/main.css'>"
        						"</head>"
        						"<body>"
        							"<b class='texto'>Kaixo</b>"
								"</body>")

class Castellano(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("<head>"
        							"<link rel='stylesheet' href='stylesheets/main.css'>"
        						"</head>"
        						"<body>"
        							"<b class='texto'>Hola</b>"
								"</body>")

class Ingles(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("<head>"
        							"<link rel='stylesheet' href='stylesheets/main.css'>"
        						"</head>"
        						"<body>"
        							"<b class='texto'>Hello</b>"
								"</body>")

class Registro(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(MAIN_PAGE_HTML)

class Comprobar(webapp2.RequestHandler):
    def post(self):
        email = self.request.get('email')
        usuarios = ndb.gql("SELECT * FROM User WHERE email=:1", email)
        if usuarios.count()==0:
           self.response.out.write("success")
        else:
           self.response.out.write("error")

class Validar(webapp2.RequestHandler):
    def post(self):
        nombre=self.request.get('nombre')
        password=self.request.get('password')
        repPassword=self.request.get('repeatPassword')
        email=self.request.get('email')

        nombreBien = True
        passwordBien = True
        passwordCoinciden = True
        emailBien = True
        todoBien = False

        self.response.out.write(MAIN_PAGE_HTML)
        
        if(nombre == ""):
            self.response.out.write("Nombre incorrecto")
            nombreBien = False

        if(len(password) < 6):
            self.response.out.write("--- La contrasena debe tener al menos 6 caracteres")
            passwordBien = False
   
        if(password != repPassword):
            self.response.out.write("--- Las contrasenas no coinciden")
            passwordCoinciden = False

        if(email == ""):
           self.response.out.write("--- El email es incorrecto")
           emailBien = False

        if(nombreBien == True and passwordBien == True and passwordCoinciden == True and emailBien == True):
            todoBien = True
        
        datos = User()
        datos.nombre = self.request.get('nombre')
        datos.email = self.request.get('email') 
        
        usuarios = ndb.gql("SELECT * FROM User WHERE email=:1", email)
        if usuarios.count()!=1 and todoBien == True:
           self.response.out.write("<b>Buenas: </b>" + nombre + ". El registro ha sido correcto.")
           datos.put()
        else:
           self.response.out.write("--- Email ya existente")

class Login(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(FORM_LOGIN)

class ComprobarLogin(session_module.BaseSessionHandler):
    def get(self):
        if self.session.get('counter'): 
            self.response.out.write('Existe una sesion activa ')
            counter = self.session.get('counter')
            self.session['counter'] = counter + 1
            self.response.out.write('Counter = ' + str(self.session.get('counter')))
        else:
            self.response.out.write('Sesion nueva')
            self.session['counter'] = 1
            self.response.out.write('Counter = ' + str(self.session.get('counter')))

class Logout(session_module.BaseSessionHandler):
    def get(self):
        del self.session['counter'] 
       
           
class SubirFoto(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(FORM_SUBIR_FOTO)

app = webapp2.WSGIApplication([
    ('/', Inicio),
    ('/kaixo', Euskara),
    ('/hola', Castellano),
    ('/hello', Ingles),
    ('/registro', Registro),
    ('/validar', Validar),
    ('/comprobar', Comprobar),
    ('/login', Login),
    ('/comprobarLogin', ComprobarLogin)

], debug=True)


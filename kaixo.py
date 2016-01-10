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
import cgi
from google.appengine.ext import ndb
from webapp2_extras import sessions
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
import session_module
import urllib
import json
import hashlib

class User(ndb.Model):
    nombre = ndb.StringProperty()
    email = ndb.StringProperty()
    password= ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    bloqueado = ndb.BooleanProperty()

class Image(ndb.Model):
    user = ndb.StringProperty()
    public = ndb.BooleanProperty()
    blob_key = ndb.BlobKeyProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    tags = ndb.StringProperty(repeated = True)
    foto_key = ndb.StringProperty()

class Album(ndb.Model):
    nombre = ndb.StringProperty()
    user = ndb.StringProperty()  

MAIN_PAGE_HTML = """\
    <head>
        <link rel='stylesheet' href='stylesheets/main.css'>
    </head>
    <body>
        <h1>Pagina inicial DSSW</h1>
        <h2>Elige tu saludo</h2>
            <a href='/kaixo'>Euskara</a><br>
            <a href='/hola'>Castellano</a><br>
            <a href='/hello'>Ingles</a><br><br>
        <h2>O registrate si quieres</h2>
            <a href='/registro'>Registro</a><br>
            <a href='/login'>Login</a><br><br>
        <h2>Album</h2>
            <a href="/fotosPublicas">Ver fotos publicas</a><br><br>
        <h2>Maps</h2>
            <a href='/maps'> Maps</a><br><br>
        <img src='images/python.jpg' height='200' width='200'>
        <br>
    </body>
"""

MAIN_PAGE_HTML_REGISTERED = """\
    <head>
        <link rel='stylesheet' href='stylesheets/main.css'>
    </head>
    <body>
        <h1>Pagina inicial DSSW</h1>
        <h2>Elige tu saludo</h2>
            <a href='/kaixo'>Euskara</a><br>
            <a href='/hola'>Castellano</a><br>
            <a href='/hello'>Ingles</a><br><br>
        <h2>Fotos</h2>
            <a href='/subir'>Subir foto</a><br>
            <a href="/fotosPublicas">Ver fotos publicas</a><br />
            <a href="/fotosPrivadas">Ver fotos privadas</a><br />
        <h3> Album </h3>
            <a href='/crearAlbum'>Crear Album</a><br>
            <a href='/anadirFoto'>Subir foto a album</a><br>
            <a href='/verFotosAlbum'>Ver fotos de album</a><br><br>
        <h2>Modificar contrasena</h2>
            <a href="/modificarPassword">Modificar password</a><br />
        <img src='images/python.jpg' height='200' width='200'>
        <br>
        <a href='logout'>Logout</a>
    </body>
"""

PAGINA_REGISTRO_HTML = """\
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
        <h1 id="titulo">DSSW</h1>
        <h2>Rellene los campos por favor:</h2>
        <form autocomplete="off" method="post" action="/validar">
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
            <input type="submit" value="Registrarse" /><br />
            <br />
            <a href="/">Volver</a>
            <a href="login">Login</a><br />
        </form>
        <div id="nombreSaludo"></div>
        </body>
    </html>
"""

FORM_LOGIN_HTML="""
<html>
  <head>
    <title>Login</title>
    <script src="https://ajax.googleapis.com/ajax/libs/prototype/1.7.2.0/prototype.js"></script>
    <script type="text/javascript">
      Event.observe(window, 'load', function(){
        Event.observe( 'login_button', 'click', formProcess);
      });
      function formProcess(){
        $('login_form').submit();
      }
    </script>
  </head>

  <body>
    <form action="/comprobarLogin" autocomplete="off" method="POST" id="login_form" name="login_form">
        <label class="etiquetas">Email: </label>
        <input id="email" name="email" type="email" />
        <label id="errorEmail"></label><br><br>
        <label class="etiquetas">Password: </label>
        <input id="password" name="password" type="password" />
        <label id="errorPassword"></label><br><br>
        <input type="button" value="Login" id="login_button" />
    </form>
    <a href="/">Volver</a><br><br>
  </body>
</html>"""

FORM_SUBIR_FOTO_HTML="""
<html>
    <body>
        <form autocomplete="off" id="subirFoto_form" action="%(url)s" method="POST" enctype="multipart/form-data">
            <input type="file" id="file" name="file"><br>
            <input type="radio" name="access" value="public" checked="checked" />    Public
            <input type="radio" name="access" value="private" /> Private<p>
            <input type="submit" id="submit" name="submit" value="Subir foto">
        </form>
    </body>
    <a href="/">Volver</a>
</html>"""

CREAR_ALBUM_HTML = """\
<html>
    <body>
        <h1>CREAR NUEVO ALBUM</h1>
          
        <form autocomplete="off" id="signUp" action="" method="POST">
              <table>
                 
                 <tr>
                      <td class="label">
                          Nombre del album
                      </td>
                      <td>
                        <input id = "album_name" type="text" name="album_name"  >
                      </td>
                      <td id="albumNameError" class="error">
                      </td>
                  </tr>
                  
              </table>
              <input type="submit" id = "submit" name="submit" value="Crear" >
            </form>
            
            <p><a href="/">Volver</a></p>
    </body>
</html>
""" 


FORM_VER_FOTOS_ALBUM_HTML = """\
<html>
    <body>
        <h1>VER FOTOS DE ALBUM</h1>
        <form autocomplete="off" id="upload" action="" method="POST">
            <h3>Escoja el album</h3>
"""  

VER_FOTOS_ALBUM_HTML = """
            <h3> Filtrar por etiqueta</h3>

            <input type="text" placeholder ="deporte, fiesta, paisaje" id="tags" name="tags" >

            <p></p>
            <div>
            <input type="submit" id = "submit" name="submit" value="Ver fotos">
            </div>
        </form>
        <a href="/">Volver</a>  
    </body>
</html>
"""


FORM_FOTO_ALBUM_HTML = """\
<html>
    <script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
  
    <body>
        <h1>Anadir foto a album</h1>

        <div id="resp"></div>      
          
        <form autocomplete="off" id="upload" action="" method="POST" enctype="multipart/form-data">
            <h3> Elige el album </h3>
"""      

FORM_SUBIR_FOTO_ALBUM_HTML = """
            <p></p>
            <h3> Elige la visibilidad</h3>
            <input type="radio" name="access" value="public" checked="checked" />    Public
            <input type="radio" name="access" value="private" /> Private<p>

            <input type="hidden" id = "key" name="key">
            
            <h3> Escribe la etiqueta que desees</h3>
            <input type="text" placeholder ="deporte, fiesta, paisaje" id="tags" name="tags" ><br>

           <p></p>
            <div>
                <input type="file" id="fileselect" name="fileselect" >
            </div>
            <p></p>
            <div>
                <input type="submit" id = "submit" name="submit" value="Anadir foto" disabled = "true">
            </div>
        </form>
  
        <script>

            $( "#fileselect" ).change(function() {
                var fd = new FormData(document.getElementById("upload"));
                $.ajax({
                  url: "%s",
                  type: "POST",
                  data: fd,
                  processData: false, 
                  contentType: false,   
                  "success": 
                    function(result) {
                        document.getElementById("key").value = result;
                        document.getElementById('submit').disabled = false;
                    }
                });
            
            });
         
        </script>
        <a href="/">Volver</a>  
    </body>
</html>
"""

MAPS_HTML="""
<html>
    <body>    
        <div class="container">
            <h1>Indica el lugar que quiere ver en el mapa</h1>
        </div>
    
        <div class="container">
        <form autocomplete="off" class="form-horizontal" method="post">
                <div class="form-group">
                    <label for="lugar" class="col-sm-2 control-label">Lugar</label>
                    <div class="col-sm-10">
                        <input placeholder="Tu ciudad" id="lugar" required type="text" name="lugar" value=""/> <br/>
                    </div>
                </div>
        </form>

        <h2 hidden id="exists_lugar"></h2>
        </div>
        
        <p id="lat"></p>
        <p id="lng"></p>
        
        <div id="map"></div>
        <script>
            var latInicial = -34.397;
            var lngInicial = 150.644;
                $(document).ready(function(){
                    $("#lugar").blur(function(){
                        $("#exists_lugar").show();
                        $.ajax({url:"/Maps",
                            data:{"lugar":$("#lugar").val()},
                            type: "post",
                            success:function(result){
                                // $("#exists_lugar").html(result);
                                var obj = eval ("("+result+")");
                                // alert(obj.lat);
                                latInicial = parseFloat(obj.lat);
                                lngInicial = parseFloat(obj.lng);
                                initMap();
                            }});
                    });
                });
            
            
            var map;
            var marker;
            function initMap() {
                map = new google.maps.Map(document.getElementById("map"), {
                    center: {lat: latInicial, lng: lngInicial},
                    zoom: 8
                });
                
                marker = new google.maps.Marker({
                    map: map,
                    draggable: false,
                    animation: google.maps.Animation.DROP,
                    position: {lat: latInicial, lng: lngInicial}
                });
            }
        </script>
        <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCMN0Kej87W3KKzEZAd0XV_m1sVXdsp29s&callback=initMap"
        async defer></script>
  </body>
</html>

"""

FORM_CAMBIAR_PASSWORD_HTML = """
<html>
   <body>
        <head>
           <title>Cambiar password</title>
        </head>

        <h1><b>Modificar password</b></h1>
        <br />
        <form autocomplete="off" action="/comprobarPassword" method="post">
            <table>
               <tr>
                    <td>Password actual</td>
                    <td><input id="password" name="password" type="password" pattern=".{6,}" required title="El password debe ser de al menos 6 caracteres"></td>
               </tr>
               <tr>
                    <td>Nuevo password</td>
                    <td><input id="new_password1" name="new_password1" type="password" pattern=".{6,}" required title="El password debe ser de al menos 6 caracteres"></td>
               </tr>
               <tr>
                    <td>Repite password</td>
                    <td><input id="new_password2" name="new_password2" type="password" placeholder="Repeat the same password"></td>
                    <td><div id="error_new_password2" class="error"></div></td>
               </tr>
            </table>
            <div><input type="submit" value="Enviar"></div>
        </form>   
        <a href="/">Volver</a>   
    </body>
</html>
"""



class Inicio(session_module.BaseSessionHandler):
    def get(self):
        if self.session.get('email'):
            self.response.out.write("<h3>" + 'Hola ' + str(self.session.get('email') + "</h3>"))
            self.response.out.write(MAIN_PAGE_HTML_REGISTERED)
        else :
            self.response.out.write(MAIN_PAGE_HTML)

class Euskara(session_module.BaseSessionHandler):
    def get(self):
        self.response.out.write("<head>"
        							"<link rel='stylesheet' href='stylesheets/main.css'>"
        						"</head>"
        						"<body>"
        							"<b class='texto'>Kaixo</b>"
								"</body>")
        if self.session.get('email'):
            self.response.out.write("<a href='logout'>Logout</a>") 

class Castellano(session_module.BaseSessionHandler):
    def get(self):
        self.response.out.write("<head>"
        							"<link rel='stylesheet' href='stylesheets/main.css'>"
        						"</head>"
        						"<body>"
        							"<b class='texto'>Hola</b>"
								"</body>")
        if self.session.get('email'):
            self.response.out.write("<a href='logout'>Logout</a>") 

class Ingles(session_module.BaseSessionHandler):
    def get(self):
        self.response.out.write("<head>"
        							"<link rel='stylesheet' href='stylesheets/main.css'>"
        						"</head>"
        						"<body>"
        							"<b class='texto'>Hello</b>"
								"</body>")
        if self.session.get('email'):
            self.response.out.write("<a href='logout'>Logout</a>") 

#-----------------------------------------------------------------------------       
# REGISTRO
#-----------------------------------------------------------------------------  
class Registro(session_module.BaseSessionHandler):
    def get(self):
        self.response.out.write(PAGINA_REGISTRO_HTML)
        if self.session.get('email'):
            self.response.out.write("<p>Debes salirte de la sesion para poder registrar</p>")
            self.response.out.write("<a href='logout'>Logout</a>")

class Comprobar(webapp2.RequestHandler):
    def post(self):
        email = cgi.escape(self.request.get('email'), quote=True)
        usuarios = ndb.gql("SELECT * FROM User WHERE email=:1", email)
        if usuarios.count()==0:
           self.response.out.write("success")
        else:
           self.response.out.write("error")

class Validar(webapp2.RequestHandler):
    def post(self):
        nombre=cgi.escape(self.request.get('nombre'), quote=True)
        password=cgi.escape(self.request.get('password'), quote=True)
        repPassword=cgi.escape(self.request.get('repeatPassword'), quote=True)
        email=cgi.escape(self.request.get('email'), quote=True)

        nombreBien = True
        passwordBien = True
        passwordCoinciden = True
        emailBien = True
        todoBien = False

        self.response.out.write(PAGINA_REGISTRO_HTML)
        
        if(nombre == ""):
            self.response.out.write("--- Nombre incorrecto")
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
        datos.nombre = cgi.escape(self.request.get('nombre'), quote=True)
        datos.email = cgi.escape(self.request.get('email'), quote=True)
        password=cgi.escape(self.request.get('password'), quote=True)
        datos.password = str(hashlib.sha224(password).hexdigest())
        datos.bloqueado = False
        
        usuarios = ndb.gql("SELECT * FROM User WHERE email=:1", email)
        if usuarios.count()!=1 and todoBien == True:
           self.response.out.write("<b>Buenas: </b>" + nombre + ". El registro ha sido correcto.")
           datos.put()
        else:
           self.response.out.write("--- Email ya existente")
#-----------------------------------------------------------------------------       
# LOGIN
#-----------------------------------------------------------------------------  
class Login(session_module.BaseSessionHandler):
    def get(self):
        self.response.out.write(FORM_LOGIN_HTML)
        if self.session.get('email'):
            self.response.out.write("<p>Debes salirte de la sesion para poder registrar</p>")
            self.response.out.write("<a href='logout'>Logout</a>")
                
class ComprobarLogin(session_module.BaseSessionHandler):
    def post(self):
        emailMetido=cgi.escape(self.request.get('email'),quote=True)
        passwordMetida=cgi.escape(self.request.get('password'),quote=True)
        passwordMetidaHash=str(hashlib.sha224(passwordMetida).hexdigest())

        usuarios = ndb.gql("SELECT * FROM User WHERE email=:1", emailMetido)

        if usuarios.count() == 0:
            self.response.out.write(FORM_LOGIN_HTML)
            self.response.out.write("No existen usuarios registrados con el email indicado")
        else:
            usuarios = usuarios.get()
            if usuarios.bloqueado == True:
                self.response.out.write(FORM_LOGIN_HTML)
                self.response.out.write("<b>Tu usuario esta bloqueado</b>")

            else:    
                password = str(usuarios.password)
                if usuarios.email==emailMetido and password==passwordMetidaHash:
                        if self.session.get('email'):
                            self.response.out.write('Hola ' + str(self.session.get('email')))
                            self.response.out.write(MAIN_PAGE_HTML_REGISTERED)
                            if self.session.get('intentos_'+emailMetido) != None:
                                del self.session['intentos_'+emailMetido]
                        else:
                            self.session['email'] = emailMetido
                            self.response.out.write('Hola ' + str(self.session.get('email')))
                            self.response.out.write(MAIN_PAGE_HTML_REGISTERED)
                            if self.session.get('intentos_'+emailMetido) != None:
                                del self.session['intentos_'+emailMetido]
                else:
                    self.response.out.write(FORM_LOGIN_HTML)

                    if self.session.get('intentos_'+emailMetido) == None:
                      self.response.out.write("Contrasena incorrecta. </br> Numero de intentos acumulados = 1")
                      self.session['intentos_'+emailMetido] = 1
                    else:
                       self.session['intentos_'+emailMetido] = self.session.get('intentos_'+emailMetido) + 1
                       intentos = str(self.session.get('intentos_'+emailMetido))
                       self.response.out.write("Contrasena incorrecta. </br> Numero de intentos acumulados = " + intentos)
                       if self.session.get('intentos_'+emailMetido) > 2:
                            usuarios.bloqueado = True
                            usuarios.put()
                            del self.session['intentos_'+emailMetido]
                            self.response.out.write("<br /><b> Se ha excedido el numero de intentos. </br> USUARIO BLOQUEADO.")


class Logout(session_module.BaseSessionHandler):
    def get(self):
        del self.session['email']
        self.response.out.write(MAIN_PAGE_HTML)

#-----------------------------------------------------------------------------       
# FOTOS
#-----------------------------------------------------------------------------              


class SubirFoto(session_module.BaseSessionHandler):
    def get(self):
        if self.session.get('email') == None:
            self.redirect("/login")
        else:

            upload_url = blobstore.create_upload_url('/almacenarFoto')
            self.response.out.write(FORM_SUBIR_FOTO_HTML % {'url':upload_url})

class ConseguirFotos(session_module.BaseSessionHandler, blobstore_handlers.BlobstoreDownloadHandler):
   def get(self, resource):
       resource = str(urllib.unquote(resource))
       blob_info = blobstore.BlobInfo.get(resource)
       self.send_blob(blob_info)

class AlmacenarFoto(session_module.BaseSessionHandler, blobstore_handlers.BlobstoreUploadHandler):            
   def post(self):
       if self.session.get('email') == None:
            self.redirect("/login")
       else:
           upload_files = self.get_uploads('file')
           blob_info = upload_files[0]
           img = Image()
           img.user = self.session.get('email')
           img.public = self.request.get("access") == "public"
           img.blob_key = blob_info.key()
           img.put()
           self.redirect("/")

class VerFotosPublicas(blobstore_handlers.BlobstoreDownloadHandler):
   def get(self):
      fotos_publicas = ndb.gql("SELECT * FROM Image WHERE public = TRUE")
      self.response.out.write('<table border="1px">')
      for foto in fotos_publicas:
        self.response.out.write('<tr><td><img src="serve/%s" width="400px" height="400px"></img></tr></td>' % foto.blob_key + '<td>' + foto.user + '</td></tr>')
      self.response.out.write('<table>')
      self.response.out.write('<a href="/">Volver</a>')

class VerFotosPrivadas(session_module.BaseSessionHandler):
   def get(self):
      useremail = self.session.get('email')
      if useremail == None:
       self.redirect("/login")
       self.response.write('Debes loguearte de nuevo')

      else:
       fotos_privadas = ndb.gql("SELECT * FROM Image WHERE public = FALSE AND user = :1", useremail)
       self.response.out.write('<table border="1px>"')
       for foto in fotos_privadas:
            self.response.out.write('<tr><td><img src="serve/%s" width="400px" height="400px"></img></tr></td>' % foto.blob_key + '<td>' + foto.user + '</td></tr>')
       self.response.out.write('</table>')
       self.response.out.write('<a href="/">Volver</a>') 


#------------------------------------------------------------------------------------------------------------------------------------
# ALBUM
# -----------------------------------------------------------------------------------------------------------------------             


class CrearAlbum(session_module.BaseSessionHandler):
    def get(self):
        if self.session.get('email'):
            self.response.write(CREAR_ALBUM_HTML)
        else:
            self.redirect("/login")
            self.response.write('Debes loguearte de nuevo')

            
    def post(self):
        if self.session.get('email'):
            albumName = cgi.escape(self.request.get('album_name'))
            
            if (len(albumName) == 0):
                self.response.write(CREAR_ALBUM_HTML)
                self.response.out.write("El nombre del album esta vacio");
            else: 
                album = Album(parent=ndb.Key('User','%s' % self.session.get('email')), id = '%s' % albumName)

                album.nombre = albumName
                album.user = self.session.get('email')
                album.put()
                self.response.write(CREAR_ALBUM_HTML)
                self.response.write('Album creado correctamente')
            
        else:
            self.redirect("/login")
            self.response.write('Debes loguearte de nuevo')

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    upload_files = self.get_uploads('fileselect')
    blob_info = upload_files[0]
    self.response.write(blob_info.key());       
    
    
class AnadirFotoAlbum(session_module.BaseSessionHandler):
    def get(self):
        if self.session.get('email'):
            upload_url = blobstore.create_upload_url('/upload')
            
            query = Album.query(ancestor= ndb.Key(User,self.session.get('email'))).fetch()
            
            self.response.out.write(FORM_FOTO_ALBUM_HTML)
            self.response.out.write('<select name = "album_name">')
            for album in query:
                self.response.out.write('<option value="%s">%s</option>' % (album.nombre,album.nombre))

            self.response.out.write('</select>')
            self.response.out.write(FORM_SUBIR_FOTO_ALBUM_HTML % upload_url)
            
        else:
            self.redirect("/login")
            self.response.write('Debes loguearte de nuevo')
            
            
    def post(self):        
        if self.session.get('email'):
            upload_url = blobstore.create_upload_url('/upload')
            imgAlbum = Image(parent= ndb.Key('User','%s' % self.session.get('email'), 'Album', '%s' % self.request.get('album_name')))
            imgAlbum.user = cgi.escape(self.session.get('email'))
            imgAlbum.foto_key = self.request.get("key")
            string = str(cgi.escape(self.request.get("tags"))).split(",")
            for tag in string:
                imgAlbum.tags.append(tag)
             
            imgAlbum.put()
            self.redirect("/")
            self.response.write('Foto subida correctamente') 
            
        else:
            self.redirect("/login")
            self.response.write('Debes loguearte de nuevo')
            

def get_first(iterable, default=None):
    if iterable:
        for item in iterable:
            return item
    return default

class VerFotosAlbum(session_module.BaseSessionHandler):
    def get(self):
        if self.session.get('email'):
            query = Album.query(ancestor= ndb.Key(User,self.session.get('email'))).fetch()
            
            self.response.out.write(FORM_VER_FOTOS_ALBUM_HTML)
            self.response.out.write('<select name = "album_name">')
            for album in query:
                self.response.out.write('<option value="%s">%s</option>' % (album.nombre,album.nombre))

            self.response.out.write('</select>')
            self.response.out.write(VER_FOTOS_ALBUM_HTML)
            
        else:
            self.redirect("/login")
            self.response.write('Debes loguearte de nuevo')
            
            
    def post(self):        
        if self.session.get('email'):
            query = Album.query(ancestor= ndb.Key(User,self.session.get('email'))).fetch()
            
            self.response.out.write(FORM_VER_FOTOS_ALBUM_HTML)
            self.response.out.write('<select name = "album_name">')
            
            for album in query:
                self.response.out.write('<option value="%s">%s</option>' % (album.nombre,album.nombre))

            self.response.out.write('</select>')
            self.response.out.write(VER_FOTOS_ALBUM_HTML)
            list = cgi.escape(self.request.get("tags")).split(",")
                     
            query = Image.query(ancestor= ndb.Key(User,self.session.get('email'), Album, cgi.escape(self.request.get('album_name')) )).fetch()
                
            for foto in query:
                if get_first(list):
                    for tag in list:
                        
                        if tag.strip() in foto.tags:
                            img = images.get_serving_url(foto.foto_key, size=None, crop=False, secure_url=True)
                            self.response.write('<tr><td><img src=%s width="400px" height="400px"></img></tr></td>' % img +'<td><p>Subida por %s ' % foto.user + '</td></tr>')
                            return
                else:
                    img = images.get_serving_url(foto.foto_key, size=None, crop=False, secure_url=True)
                    self.response.write('<tr><td><img src=%s width="400px" height="400px"></img></tr></td>' % img +'<td><p>Subida por %s ' % foto.user + '</td></tr>')
                    
        else:
            self.redirect("/login")
            self.response.write('Debes loguearte de nuevo')
            

                     
# ----------------------------------------------------------------------------
# MAPA
# ----------------------------------------------------------------------------

class Mapa(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(MAPS_HTML)
        
    def post(self):
        serviceurl = 'http://maps.googleapis.com/maps/api/geocode/json?'
        address=cgi.escape(self.request.get('lugar'))
        url = serviceurl + urllib.urlencode({'address': address})
        
        uh = urllib.urlopen(url)
        data = uh.read()
        
        js = json.loads(str(data))
        location = js['results'][0]['geometry']['location']
        lat = str(js['results'][0]['geometry']['location']['lat'])
        lng = str(js['results'][0]['geometry']['location']['lng'])
        lat_long = {"La latitud es:":lat, "La longitud es:":lng}
        self.response.out.write("<h3>" + address + "</h3>")        
        self.response.out.write(lat_long) 
        self.response.out.write("<br><br><a href='/'>Volver</a>")        

# ---------------------------------------------------------------------------------
#   MODIFICAR PASSWORD
# ---------------------------------------------------------------------------------
class ModificarPassword(session_module.BaseSessionHandler):
   def get(self):
      if self.session.get('email') == None:
       self.redirect("/login")
      else:
       self.response.out.write(FORM_CAMBIAR_PASSWORD_HTML)

class ComprobarPassword(session_module.BaseSessionHandler):
    def post(self):
      emailUsuario = self.session.get('email')
      if emailUsuario == None:
        self.redirect("/login")
      else:
       password = cgi.escape(self.request.get('password'),quote=True)
       passwordSHA = str(hashlib.sha224(password).hexdigest())
       usuario_cambiar = ndb.gql("SELECT * FROM User WHERE email = :1 AND password = :2", emailUsuario, passwordSHA)
            
       if usuario_cambiar.count() == 0:
          self.response.out.write(FORM_CAMBIAR_PASSWORD_HTML)
          self.response.out.write("<p>El password actual es incorrecto</p>")
       else:
          new_password1 = cgi.escape(self.request.get('new_password1'),quote=True)
          new_password2 = cgi.escape(self.request.get('new_password2'),quote=True)
          if(len(new_password1) < 6):
            self.response.out.write("--- La contrasena debe tener al menos 6 caracteres")
          else:  
              if new_password1 != new_password2:
               self.response.out.write(FORM_CAMBIAR_PASSWORD_HTML)
               self.response.out.write("<p>Los passwords nuevos no coinciden</p>")
              else:
                if password == new_password1:
                    self.response.out.write(FORM_CAMBIAR_PASSWORD_HTML)
                    self.response.out.write("<p>El nuevo password debe ser distinto al anterior</p>")
                else:
                    newPasswordSHA = str(hashlib.sha224(new_password1).hexdigest())
                    usuario_cambiar.get().password = newPasswordSHA
                    usuario_cambiar.get().put()
                    self.response.out.write(FORM_CAMBIAR_PASSWORD_HTML)
                    self.response.out.write("<p>El password se ha modificado correctamente!!</p>")       

app = webapp2.WSGIApplication([
    ('/', Inicio),
    ('/kaixo', Euskara),
    ('/hola', Castellano),
    ('/hello', Ingles),
    ('/registro', Registro),
    ('/validar', Validar),
    ('/comprobar', Comprobar),
    ('/login', Login),
    ('/comprobarLogin', ComprobarLogin),
    ('/maps', Mapa),
    ('/logout', Logout),
    ('/subir', SubirFoto),
    ('/almacenarFoto', AlmacenarFoto),
    ('/fotosPublicas', VerFotosPublicas),
    ('/fotosPrivadas', VerFotosPrivadas), 
    ('/serve/([^/]+)?', ConseguirFotos),
    ('/upload', UploadHandler),
    ('/crearAlbum', CrearAlbum),
    ('/anadirFoto', AnadirFotoAlbum),
    ('/verFotosAlbum', VerFotosAlbum),
    ('/modificarPassword', ModificarPassword),
    ('/comprobarPassword', ComprobarPassword),

    

], debug=True, config=session_module.myconfig_dict)

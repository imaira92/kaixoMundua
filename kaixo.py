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

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("<link rel='stylesheet' type='text/css' href='estilos.css'><b class='texto'>kaixo</b><img src='images.jpg' height='800' width='600'>")

class MainHandler2(webapp2.RequestHandler):
    def get(self):
        self.response.write("<link rel='stylesheet' type='text/css' href='estilos.css'><b class='texto'>hola</b><img src='images.jpg' height='800' width='600'>")

class MainHandler3(webapp2.RequestHandler):
    def get(self):
        self.response.write("<link rel='stylesheet' type='text/css' href='estilos.css'><b class='texto'>hello</b><img src='images.jpg' height='800' width='600'>")

app = webapp2.WSGIApplication([
    ('/kaixo', MainHandler),
    ('/hola', MainHandler2),
    ('/hello', MainHandler3)
], debug=True)


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
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Post(db.Model):   #create data table for all blog posts using a class
    title = db.StringProperty(required = True) #constraint
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainHandler(Handler):
    def get(self):
        self.redirect('/blog')

class BlogList(Handler):
    def render_bloglist(self, blogs=""):
        blogs = db.GqlQuery("SELECT * FROM Post "
                           "ORDER BY created DESC LIMIT 5 ")

        self.render("view.html", blogs=blogs)

    def get(self):
        self.render_bloglist()

class NewPost(Handler):
    def render_main(self, title="", body="", error=""):
        #blogs = db.GqlQuery("SELECT * FROM Blog "
        #                    "ORDER BY created DESC ")
        self.render("main.html", title=title, body=body, error=error) #arts=arts)

    def get(self):
        #self.redirect('/newpost')
        self.render_main()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            p = Post(title=title, body=body)
            p.put()
            self.redirect("/blog/"+str(p.key().id()))
        else:
            error = "Please enter both a title and a body!"
            self.render_main(title, body, error = error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        post = Post.get_by_id(int(id))
        t = jinja_env.get_template("single-view.html")
        if post:
            title = post.title
            body = post.body
            content = t.render(single_title = title, single_body = body, error = "")
            self.response.write(content)
        else:
            error = "Post ID does not exist"
            content = t.render(single_title = "", single_body = "", error = error)
            self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', BlogList),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)

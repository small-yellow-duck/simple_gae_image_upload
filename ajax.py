import os, sys #, cgi, urlparse, json
sys.path.append("lib")
import jinja2, webapp2, urllib, urllib2

from google.appengine.api import urlfetch #users, oauth,
from webapp2_extras import sessions

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import google.appengine.api.images as images

template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
            # To set a value:
            # self.session['img_url'] = 'http://small-yellow-duck.github.io/circles/starry_night.jpg'

        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        # Here is where the problem was - the `return` was missing
        sess = self.session_store.get_session()
        if not sess.get('img_url'):
            sess['img_url']='http://small-yellow-duck.github.io/circles/starry_night.jpg'
        #return self.session_store.get_session()
        return sess



class MainPage(BaseHandler):
	
	def get(self):
		img_url = self.session.get('img_url')
    	
    	#img_url = self.request.get("img_url")
#    	if not img_url:
#     		img_url = 'http://small-yellow-duck.github.io/circles/starry_night.jpg'
		
		outline=''
		upload_url = blobstore.create_upload_url('/upload')
		
		template = template_env.get_template('index.html')
		context = {
			'upload_url': upload_url,
			'img_src' : img_url,
		}
		self.response.write(template.render(context))


		
			

class UploadHandler(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):

		
	def post(self):
		upload_files = self.get_uploads('upload')
		if not upload_files:
			self.redirect('/')
		else:
			blob_info = upload_files[0]
	
			#self.redirect('/serve/%s' % blob_info.key())
	
			img_url = images.get_serving_url(blob_info.key())
			print img_url
			#img_url = blob_info.key()

			self.session['img_url']	= img_url
			
	
			upload_url = blobstore.create_upload_url('/upload')
	
			template = template_env.get_template('index.html')
			context = { 
				'upload_url': upload_url,
				'img_src': self.session.get('img_url')
			}
			self.response.write(template.render(context))
			
		print 'upload handler ',  self.session.get('img_url')
		#self.redirect('/')
		

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}




app = webapp2.WSGIApplication([
    ('/', MainPage),
	('/upload', UploadHandler)], debug=True, config=config)
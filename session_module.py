#Import sessions for session handling
import webapp2
from webapp2_extras import sessions

#This is needed to configure the session secret key
#Runs first in the whole application
myconfig_dict = {}
myconfig_dict['webapp2_extras.sessions'] = {
    'secret_key': '1234',
}

#Session Handling class, gets the store, dispatches the request
class BaseSessionHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session(name=None, max_age=300, factory=None, backend='securecookie')
#End of BaseSessionHandler Class

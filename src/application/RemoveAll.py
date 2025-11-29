# -*- coding: utf-8 -*-
#from google.appengine.ext import webapp
import webapp2
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from models import ziplist
from models import station
from models import bkdata
from models import member
from models import message
from models import msgcombinator
import timemanager
from google.appengine.api import memcache

class RemoveAll(webapp2.RequestHandler):
#https://www.my-notebook.net/google/gae-remove-datastore.html

    bookmark = ''
    def get(self) :

        self.bookmark = self.request.get("bookmark")
        self.skip = self.request.get("skip")
        limit = 999

        mylist=self.getMyList(limit,self.bookmark,self.skip)
        if mylist.count() < 1 :
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write( 'OK all jobs complete.' )
            return
        i = 0
        for c in mylist.fetch(limit):
            c.put()
#            c.delete()
            memcache.set("changedlog", i)
            self.bookmark = str(c.bkID)


        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write( '<html>' )
        self.response.out.write( '<head>' )
        if self.bookmark:
            self.response.out.write( '<META HTTP-EQUIV="REFRESH" CONTENT="10;URL=/RemoveAll?bookmark=' + self.bookmark + '">')
        else:
            self.response.out.write( '<META HTTP-EQUIV="REFRESH" CONTENT="10;URL=/RemoveAll">')
        self.response.out.write( '</head>' )
        self.response.out.write( '<body>' )
        self.response.out.write( 'Again after 10seconds.' )
        self.response.out.write( '</body>' )
        self.response.out.write( '</html>' )


    def getMyList(self,limit,bookmark=None,skip=None):

#        query = station.Line.gql("LIMIT " + str(limit))

#        query = ziplist.ziplist.gql("WHERE zipcode > '" + self.bookmark + "' ORDER BY zipcode LIMIT " + str(limit))

#        query = ziplist.ziplist.gql('WHERE zipcode = null LIMIT '+ str(limit))

#        query = station.Station.gql('LIMIT '+ str(limit))

        if bookmark:
            query = bkdata.BKdata.gql(u"WHERE bkID > '" + bookmark + "' ORDER BY bkID LIMIT " + str(limit))
        else:
            query = bkdata.BKdata.gql(u"ORDER BY bkID LIMIT " + str(limit))

        """
        if bookmark:
            query = msgcombinator.msgcombinator.gql(u"WHERE __key__ => '" + bookmark + "' and combkind = ''  ORDER BY __key__ LIMIT " + str(limit))
        else:
            query = msgcombinator.msgcombinator.gql(u"WHERE combkind = '' ORDER BY __key__ LIMIT " + str(limit))
        """
#        if bookmark:
#            suggestions = Suggestion.all().order("__key__").filter('__key__ >=', bookmark).fetch(PAGESIZE+1)
#        else:
#            suggestions = Suggestion.all().order("-when").fetch(PAGESIZE+1)
        """
        if bookmark:
            query = member.member.gql("WHERE phone = null AND memberID > '" + bookmark + "' ORDER BY memberID LIMIT " + str(limit))
        else:
            query = member.member.gql("WHERE phone = null ORDER BY memberID LIMIT " + str(limit))
        """

#        res = query[0:min(query.count(),limit)]
#        return res
        return query

application = webapp2.WSGIApplication(
    [
        ('/RemoveAll', RemoveAll)
    ],
    debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
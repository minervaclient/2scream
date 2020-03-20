# PROTOTYPE for logginging into myCourses (formatting will be a mess for a while)

from __future__ import absolute_import
from __future__ import unicode_literals

from minerva_common import *
from grades import *
from content import *
import shib_credentials

import sys
import re


import logging

# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


def shibboleth_login():
    """ Ask myCourses for a shibboleth based login """

    # Request shibboleth redirect
    r1 = minerva_get('Shibboleth.sso/Login?entityID=%s/idp/shibboleth' % shib_credentials.idp_url, base_url=shib_credentials.lms_url)
    shibboleth_dummy_page = minerva_parser(r1.text)
    shibboleth_form_url = shibboleth_dummy_page.find('form', {'name': 'form1'}).attrs['action']

    # Do a pointless post to get a login page
    r2 = minerva_post(shibboleth_form_url, shibboleth_dummy_post(), base_url=shib_credentials.idp_url)
    shibboleth_login_page = minerva_parser(r2.text)
    shibboleth_login_url = shibboleth_login_page.find('form').attrs['action']
    login_req = {'j_username': shib_credentials.username, 'j_password': shib_credentials.password, '_eventId_proceed': 'Log in'}

    # Do a request to log in
    r3 = minerva_post(shibboleth_login_url, login_req, base_url=shib_credentials.idp_url)
    authz_form = minerva_parser(r3.text).find('form')
    mycourses_callback = authz_form.attrs['action']
    param_relaystate = authz_form.find('input', {'name': 'RelayState'}).attrs['value']
    param_samlresponse = authz_form.find('input', {'name': 'SAMLResponse'}).attrs['value']
    authz_req = {'RelayState': param_relaystate, 'SAMLResponse': param_samlresponse}
    
    # Inform myCourses that we are now in
    r4 = minerva_post(mycourses_callback, authz_req, base_url='')

    # Just get this random URL so myCourses knows we're in
    r5 = minerva_get('d2l/lp/auth/login/ProcessLoginActions.d2l', base_url=shib_credentials.lms_url)


    # At this point, we're officially in. r5.text holds some html goop we can use, along with further authorization steps to see a list of courses
    # It is so much less painful to see info about particular courses if you know their code. As a POC, let's get some info from URBP201
    class_code = sys.argv[1] 
    # This is the list of assignments
    r6 = minerva_get("d2l/lms/grades/my_grades/main.d2l?ou=%s" % (class_code), base_url=shib_credentials.lms_url)
    
    print (as_json(dump_grades(r6.text)))


    r7 = minerva_get("d2l/le/content/%s/Home" % (class_code), base_url=shib_credentials.lms_url)

    print(download_stuff(r7.text,class_code))
    print(type(r7.text))
    

    
    


def shibboleth_dummy_post():
    """ We have to send this nonsense back to shibboleth to get the actual login form """
    return "shib_idp_ls_exception.shib_idp_session_ss=&shib_idp_ls_success.shib_idp_session_ss=false&shib_idp_ls_value.shib_idp_session_ss=&shib_idp_ls_exception.shib_idp_persistent_ss=&shib_idp_ls_success.shib_idp_persistent_ss=false&shib_idp_ls_value.shib_idp_persistent_ss=&shib_idp_ls_supported=&_eventId_proceed="


shibboleth_login() 

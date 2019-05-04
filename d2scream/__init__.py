from . import login_shibboleth
from . import course_ids
from . import grades as grades_mod
from . import assign as assign_mod

class CourseActions():
    def __init__(self,creds,ou):
        self.creds = creds
        self.ou = ou

    def grades(self):
        return grades_mod.dump(self.creds,self.ou)
    def assignments(self):
        return assign_mod.dump(self.creds,self.ou)


class Client():
    def __init__(self,creds):
        self.creds = creds

    def courses(self):
        return course_ids.dump(self.creds)

    def grades(self,ou):
        return grades_mod.dump(self.creds,ou)
    
    def assignments(self,ou):
        return assign_mod.dump(self.creds,ou)

    def using(self,course):
        return CourseActions(self.creds, course.ou)

def login(creds):
    login_shibboleth.login(creds)
    return Client(creds)

def login_saved():
    from . import shib_credentials
    return login(shib_credentials)

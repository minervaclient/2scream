from __future__ import absolute_import
from __future__ import unicode_literals

import d2scream

def menu(courses):
    for counter, course in zip(range(1,len(courses) + 1), courses):
        print("#%2d: %6s = %s" % (counter, course.ou, course.course))
    
    return courses[int(input("====> ")) - 1]

def demo1():
    d2s = d2scream.login_saved()
    courses = d2s.courses()
    for course in courses[1:]:
        print(course.course, "###")
        grades = d2s.using(course.ou).grades()
        print(grades.json())

        assigns = d2s.using(course.ou).assignments()
        print(assigns.json())

def demo2():
    d2s = d2scream.login_saved()
    courses = d2s.courses()
    course = menu(courses)
    course = d2s.using(course.ou)
    print(course.grades().sql())
    print(course.assignments().sql())


demo2()

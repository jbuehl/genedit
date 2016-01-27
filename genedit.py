#!/usr/bin/python

import cgi, cgitb, sys, time, os, Cookie
from genconf import *
from genenv import *
from genclasses import *
from gendisplay import *
from geneditedit import *
from genupdate import *
from gendelete import *
from genutils import *

###############################################################################
# user functions
###############################################################################

def identifyUser():
    userName = ""
    try:	# if there is a cookie, get the username
        cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE"))
        userName = cookie["genedit-username"].value
    except:
        if domain == "localhost":   # testing
            userName = "Joe"
        #pass
    return userName

def loginUser(theContext):
    outFile = theContext.outFile
    outFile.printHtmlHeader("Please login", "onLoad='document.forms.login.username.focus()'")
    if debugForm: print form
    outFile.write("<h1>Please login</h1>")
    outFile.write("In order to make changes, please enter your first name.<br>")
    outFile.write("The purpose of this is to be able to track changes.<br>")
    outFile.write("You should only need to enter this once per computer that you are using.<br>")
    outFile.write("<br>")
    outFile.write('<form name="login" action="'+scriptName+'" method="post">')
    outFile.write('Please enter your name: ')
    outFile.write('<input type="text" name="username" />')
    outFile.write('<input type="submit" name="function" value="Login" />')
    outFile.write('<input type="hidden" name="id" value="'+theContext.thePerson.id+'"/>')
    #outFile.write('<input type="hidden" name="lastid" value="'+theContext.lastId+'"/>')
    outFile.write('<input type="hidden" name="lastfunction" value="'+theContext.function+'"/>')
    outFile.write("</form>")

def getUser(theContext):
    userName = theContext.form.getfirst("username").split()[0]  # split off the first name
    # set a cookie that contains the user name
    cookie = Cookie.SimpleCookie()
    cookie["genedit-username"] = userName
    cookie["genedit-username"]["domain"] = domain
    cookie["genedit-username"]["path"] = "/"
    cookie["genedit-username"]["expires"] = "Fri, 29-Nov-2030 00:00:00 GMT"
    theContext.outFile.write(cookie.output()+"\n")
    theContext.function = theContext.form.getfirst("lastfunction")  # restore the function
    return userName

def getIndexedFunction(thePerson, function):
    index = 0
    # the function key specifies which button was pressed to submit the form
    if function == "":      # the button was related to a particular spouse
        for spouseIndex in range(len(thePerson.familySpouse)):
            function = form.getfirst("functionS"+str(spouseIndex), "")
            if function == removeFunction:
                function = removeSpouseFunction
                index = spouseIndex
                break
    if function == "":      # the button was related to a particular image
        for imageIndex in range(len(thePerson.images)):
            function = form.getfirst("functionI"+str(imageIndex), "")
            if function == removeFunction:
                function = removeIndexFunction
                index = imageIndex
                break
    return (function, index)
    
###############################################################################
# main program
###############################################################################

if __name__ == "__main__":
    global persons, families, outFile, logFile, form, function, functionIndex, userName

    # initialization
    persons = {"I000": person("I000", "unknown", "unknown")}
    families = {}
    errorMsg = ""
    outFile = htmlFile("sys.stdout", "w", urlPath)
    logFile = logFile(logFileName)
    
    # start getting the form values    
    cgitb.enable()
    form = cgi.FieldStorage()

    function = form.getfirst("function", "")
    lastId = form.getfirst("lastid", "I000")
    personId = form.getfirst("id", "")
    if personId != "":
        # read all the data for the specified person and immediate relatives
        thePerson = person(personId)
        persons[personId] = (thePerson)
        thePerson.readPersonFromFile()
        readRelatives(thePerson, persons, families)
        (function, functionIndex) = getIndexedFunction(thePerson, function)
    else:
        thePerson = None
        functionIndex = 0
                
    # if there is no function specified, display the list of people
    if (function == "") & (personId == ""):
        function = peopleFunction

    theContext = context(persons, families, outFile, logFile, form, thePerson, function, functionIndex, identifyUser())
    
    if function == loginFunction:
        getUser(theContext)

    if (function == editFunction) | (function in updateFunctions):
        # functions that modify data require a user name
        if theContext.userName == "":
            loginUser(theContext)
        else:
            if function != editFunction:
                errorMsg = updatePerson(theContext)
            editPerson(theContext, errorMsg)
        
    # functions that only display data
    elif function == peopleFunction:
        displayPeople(theContext)
    elif function == descendantsFunction:
        displayDescendants(theContext)
    elif function == ancestorsFunction:
        displayAncestors(theContext)
    else:   # anything else defaults to display
        displayPerson(theContext)
        
    outFile.printHtmlTrailer()




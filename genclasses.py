#!/usr/bin/python

#  genealogy.py
#  
#
#  Created by Joe Buehl on 9/8/11.
#  Copyright 2011 Buehl Technology. All rights reserved.

import sys, os, time, string
from genconf import *
from genenv import *

def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")
    
# class definitions

###############################################################################
# context
###############################################################################
class context:
    def __init__(self, persons, families, outFile, logFile, form, thePerson, function, functionIndex, userName):
        self.persons = persons
        self.families = families
        self.outFile = outFile
        self.logFile = logFile
        self.form = form
        self.thePerson = thePerson
        self.function = function
        self.functionIndex = functionIndex
        self.userName = userName

    def getValues(self):
        return (self.persons, self.families, self.outFile, self.logFile, self.form, self.thePerson, self.function, self.functionIndex, self.userName)
       
###############################################################################
# gedcomFile
###############################################################################
class gedcomFile:
    def __init__(theFile, fileName):
        if debug: print "gedcomFile:", fileName
        theFile.fileName = fileName

    def openFile(theFile, mode="r"):
        if debug: print "openFile:", mode
        theFile.file = open(filePath+theFile.fileName, mode)
    
    def closeFile(theFile):
        if debug: print "closeFile:"
        theFile.file.close()
    
    def readFile(theFile, persons, families):
        if debug: print "readFile:"
        theFile.readLine()
        while theFile.level >= 0:
            if theFile.tag == "INDI":
                thePerson = person(theFile.value)
                thePerson.file = theFile
                persons[theFile.value] = (thePerson)
                thePerson.readPerson()
            elif theFile.tag == "FAM":
                theFamily = family(theFile.value)
                theFamily.file = theFile
                families[theFile.value] = (theFamily)
                theFamily.readFamily()
            elif theFile.tag == "HEAD":
                theFile.readHeader()
            elif theFile.tag == "TRLR":
                theFile.readLine()
            elif theFile.tag == "SUBM":
                theFile.readLine()
            else:
                print "Unrecognized level 0 tag", theFile.tag
                theFile.readLine()
    
    def readHeader(theFile):
        if debug: print "readHeader:"
        theFile.readLine()
        while theFile.level > 0:
            theFile.readLine()

    def readLine(theFile):
        theFile.line = theFile.file.readline().strip("\n").strip("\r")
        if theFile.line:
            theFile.fields = theFile.line.split()
            theFile.level = int(theFile.fields[0])
            if theFile.level == 0:
                if theFile.fields[1][0] == "@":
                    theFile.value = theFile.fields[1].strip("@")
                    theFile.tag = theFile.fields[2]
                else:
                    theFile.tag = theFile.fields[1]
                    theFile.value = ""
            else:
                theFile.tag = theFile.fields[1]
                theFile.value = theFile.line[len(theFile.tag)+3:]
        else:
            theFile.level= -1
            theFile.tag = ""
            theFile.value = ""
        if debug: print "readLine: level:", theFile.level, "tag:", theFile.tag, "value", theFile.value
 
    def writeLine(theFile, level, tag="", value=""):
        if debug: print "writeLine:", level, tag, value
        theFile.file.write(str(level)+" "+tag+" "+value+"\n")

    def deleteFile(theFile, userName, logFile):
        os.renames(filePath+theFile.fileName, deletedPath+timestamp()+theFile.fileName)
        logFile.log(userName, "delete", theFile.fileName)

###############################################################################
# logFile
###############################################################################
class logFile:
    def __init__(theFile, fileName):
        if debug: print "logFile:", fileName
        theFile.fileName = fileName

    def log(theFile, userName, operation, fileName):
        theFile.file = open(filePath+theFile.fileName, "a")
        theFile.file.write("%-12s %-8s %-8s %-20s\n" % (userName, operation, fileName, timestamp()))
        theFile.file.close()
    
###############################################################################
# htmlFile
###############################################################################
class htmlFile:
    def __init__(theFile, fileName, mode, url=""):
        if debug: print "htmlFile:", fileName, mode
        if fileName == "sys.stdout":
            theFile.file = sys.stdout
        else:
            theFile.file = open(filePath+fileName, mode)
        theFile.url = url
        
    def write(theFile, buffer):
        if debug: print "htmlWrite:", buffer
        theFile.file.write(buffer)
    
    def printHtmlHeader(theFile, title, body=""):
        if debug: print "printHtmlHeader:", title
        theFile.write("Content-Type: text/html\n\n")
        theFile.write('<!DOCTYPE html PUBLIC \n') 
        theFile.write('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" >\n')
        theFile.write('<head>\n') 
        theFile.write('<title>'+title+' - Family</title>\n')
        theFile.write('</head><body BGCOLOR="#ffffff" '+body+'>\n')
	
    def printHtmlTrailer(theFile):
        if debug: print "printHtmlTrailer:"
        theFile.write('<font size="1" >v'+version+'</font>')
        theFile.write('</body></html>\n')
	    
###############################################################################
# person
###############################################################################
class person:
    def __init__(thePerson, id, name = "", surname = "", sex = ""):
        if debug: print "person:", id, name, surname, sex
        thePerson.id = id
        thePerson.file = gedcomFile(id+".ged")
        thePerson.name = name
        thePerson.surname = surname
        thePerson.sex = sex
        thePerson.birth = event(date(""))
        thePerson.christened = event()
        thePerson.death = event()
        thePerson.buried = event()
        thePerson.familyChild = ""
        thePerson.familySpouse = []
        thePerson.note = note("")
        thePerson.occupation = ""
        thePerson.images = []

    def __del__(thePerson):
        if debug: print "~person:"
        del thePerson.file   
		
    def readPersonFromFile(thePerson):
        if debug: print "readPersonFromFile:"
        thePerson.file.openFile()
        thePerson.file.readLine()
        thePerson.readPerson()
        thePerson.file.closeFile()
        
    def readPerson(thePerson):
        if debug: print "readPerson:"
        thePerson.file.readLine()
        while thePerson.file.level > 0:
            if thePerson.file.tag == "NAME":
                names = thePerson.file.value.split("/")
                thePerson.name = names[0].strip()
                thePerson.surname = names[1]
                thePerson.file.readLine()
            elif thePerson.file.tag == "SEX":
                thePerson.sex = thePerson.file.value
                thePerson.file.readLine()
            elif thePerson.file.tag == "FAMC":
                thePerson.familyChild = thePerson.file.value.strip("@")
                thePerson.file.readLine()
            elif thePerson.file.tag == "FAMS":
                thePerson.familySpouse.append(thePerson.file.value.strip("@"))
                thePerson.file.readLine()
            elif thePerson.file.tag == "BIRT":
                thePerson.birth.readEvent(thePerson.file, thePerson.file.level)
            elif thePerson.file.tag == "DEAT":
                if thePerson.death is None:
                    thePerson.death = event()
                thePerson.death.readEvent(thePerson.file, thePerson.file.level)
            elif thePerson.file.tag == "CHR":
                if thePerson.christened is None:
                    thePerson.christened = event()
                thePerson.christened.readEvent(thePerson.file, thePerson.file.level)
            elif thePerson.file.tag == "BURI":
                if thePerson.buried is None:
                    thePerson.buried = event()
                thePerson.buried.readEvent(thePerson.file, thePerson.file.level)
            elif thePerson.file.tag == "NOTE":
                thePerson.note = note(thePerson.file.value)
                thePerson.note.readNote(thePerson.file, thePerson.file.level)
            elif thePerson.file.tag == "OCCU":
                thePerson.occupation = thePerson.file.value
                thePerson.file.readLine()
            elif thePerson.file.tag == "OBJE":
                theImage = image()
                theImage.readImage(thePerson.file, thePerson.file.level)
                thePerson.images.append(theImage)
            else:
                print "Unrecognized person tag", thePerson.file.tag

    def writePersonToFile(thePerson, userName, logFile):
        if debug: print "writePersonToFile:"
        if (userName != "") & (os.path.exists(filePath+thePerson.file.fileName)):
            os.renames(filePath+thePerson.file.fileName, deletedPath+timestamp()+thePerson.file.fileName)
        thePerson.file.openFile("w")
        thePerson.writePerson(0)
        if userName != "":
            logFile.log(userName, "write", thePerson.file.fileName)
        thePerson.file.closeFile()
        
    def writePerson(thePerson, level):
        if debug: print "writePerson:"
        thePerson.file.writeLine(level, "@"+thePerson.id+"@", "INDI")
        level += 1
        thePerson.file.writeLine(level, "NAME", thePerson.name+" /"+thePerson.surname+"/")
        if thePerson.sex != "":
            thePerson.file.writeLine(level, "SEX", thePerson.sex)
        if thePerson.familyChild != "":
            thePerson.file.writeLine(level, "FAMC", "@"+thePerson.familyChild+"@")
        for familySpouse in thePerson.familySpouse:
            if familySpouse != "":
                thePerson.file.writeLine(level, "FAMS", "@"+familySpouse+"@")
        thePerson.birth.writeEvent(thePerson.file, level, "BIRT")
        if thePerson.death.date.year != "":
            thePerson.death.writeEvent(thePerson.file, level, "DEAT")
#        if thePerson.christened is not None:
#            thePerson.christened.writeEvent(theFile, level, "CHR")
#        if thePerson.buried is not None:
#            thePerson.buried.writeEvent(theFile, level, "BURI")
        if thePerson.note.value != "":
            thePerson.note.writeNote(thePerson.file, level)
        if thePerson.occupation != "":
            thePerson.file.writeLine(level, "OCCU", thePerson.occupation)
        for theImage in thePerson.images:
            theImage.writeImage(thePerson.file, level)
                        
    def printPersonLink(thePerson, urlPath, function="Display", lastId=""):
        return '<a href="'+urlPath+thePerson.id+'&lastid='+lastId+'&function='+function+'">'+thePerson.name+" "+thePerson.surname+'</a>'
	
    def printPersonBrief(thePerson, urlPath, lastId="I000"):
        if thePerson.birth.date.isValid():
            birth = thePerson.birth.date.year
        else:
            birth = "unknown"
        if thePerson.death.date.isValid():
            death = thePerson.death.date.year
        else:
            death = ""
        return thePerson.printPersonLink(urlPath, "Display", lastId)+"  "+birth+" - "+death
	
    def printPersonIndent(thePerson, urlPath, level, levelDisp, indentDisp):
	    indent = ""
	    for i in range(level-1):
	        indent += indentDisp
	    return indent+levelDisp+" "+thePerson.printPersonBrief(urlPath)
	
###############################################################################
# family
###############################################################################
class family:
    def __init__(theFamily, id, husband = "", wife = ""):
        if debug: print "family:", id, husband, wife
        theFamily.id = id
        theFamily.file = gedcomFile(id+".ged")
        theFamily.husband = husband
        theFamily.wife = wife
        theFamily.marriage = event()
        theFamily.engaged = event()
        theFamily.children = []
        theFamily.note = note("")

    def __del__(theFamily):
        if debug: print "~family:"
        del theFamily.file   
		
    def readFamilyFromFile(theFamily):
        theFamily.file.openFile()
        theFamily.file.readLine()
        theFamily.readFamily()
        theFamily.file.closeFile()
        
    def readFamily(theFamily):
        if debug: print "readFamily:"
        theFamily.file.readLine()
        while theFamily.file.level > 0:
            if theFamily.file.tag == "HUSB":
                theFamily.husband = theFamily.file.value.strip("@")
                theFamily.file.readLine()
            elif theFamily.file.tag == "WIFE":
                theFamily.wife = theFamily.file.value.strip("@")
                theFamily.file.readLine()
            elif theFamily.file.tag == "MARR":
                if theFamily.marriage is None:
                    theFamily.marriage = event()
                theFamily.marriage.readEvent(theFamily.file, theFamily.file.level)
            elif theFamily.file.tag == "CHIL":
                theFamily.children.append(theFamily.file.value.strip("@"))
                theFamily.file.readLine()
            elif theFamily.file.tag == "ENGA":
                if theFamily.engaged is None:
                    theFamily.engaged = event()
                theFamily.engaged.readEvent(theFamily.file, theFamily.file.level)
            elif theFamily.file.tag == "NOTE":
                theFamily.note = note(theFamily.file.value)
                theFamily.note.readNote(theFamily.file, theFamily.file.level)
            else:
                print "Unrecognized family tag", theFamily.file.tag

    def writeFamilyToFile(theFamily, userName, logFile):
        if debug: print "writeFamilyToFile:"
        if (userName != "") & (os.path.exists(filePath+theFamily.file.fileName)):
            os.renames(filePath+theFamily.file.fileName, deletedPath+timestamp()+theFamily.file.fileName)
        theFamily.file.openFile("w")
        theFamily.writeFamily(0)
        if userName != "":
            logFile.log(userName, "write", theFamily.file.fileName)
        theFamily.file.closeFile()
        
    def writeFamily(theFamily, level):
        if debug: print "writeFamily:"
        theFamily.file.writeLine(level, "@"+theFamily.id+"@", "FAM")
        level += 1
        if theFamily.husband != "":
            theFamily.file.writeLine(level, "HUSB", "@"+theFamily.husband+"@")
        if theFamily.wife != "":
            theFamily.file.writeLine(level, "WIFE", "@"+theFamily.wife+"@")
        for child in theFamily.children:
            theFamily.file.writeLine(level, "CHIL", "@"+child+"@")
        if theFamily.marriage.date.year is not "":
            theFamily.marriage.writeEvent(theFamily.file, level, "MARR")
        if theFamily.engaged.date.year is not "":
            theFamily.engaged.writeEvent(theFamily.file, level, "ENGA")
        if theFamily.note.value is not "":
            theFamily.note.writeNote(theFamily.file, level)

###############################################################################
# event
###############################################################################
class event:
    def __init__(theEvent, theDate=None, place="", cause=""):
        if debug: print "event:", theDate, place, cause
        if theDate == None:
            theEvent.date = date("")
        else:
            theEvent.date = theDate
        theEvent.place = place
        theEvent.cause = cause
        
    def readEvent(theEvent, theFile, lastLevel):
        if debug: print "readEvent:", lastLevel
        theFile.readLine()
        while theFile.level > lastLevel:
            if debug: print "Event:", theFile.level, theFile.tag, theFile.value
            if theFile.tag == "DATE":
                theEvent.date = date(theFile.value)
                if not theEvent.date.isValid():
                    pass
                    #print "Invalid date", theFile.value
            elif theFile.tag == "PLAC":
                theEvent.place = theFile.value
            elif theFile.tag == "CAUS":
                theEvent.cause = theFile.value
            else:
                print "Unrecognized event tag", theFile.tag            
            theFile.readLine()

    def writeEvent(theEvent, theFile, level, tag):
        if debug: print "writeEvent:", level, tag
        theFile.writeLine(level, tag)
        level += 1
        if theEvent.date.year != "":
            theFile.writeLine(level, "DATE", theEvent.date.normalize())
        if theEvent.place != "":
            theFile.writeLine(level, "PLAC", theEvent.place)
        if theEvent.cause != "":
            theFile.writeLine(level, "CAUS", theEvent.cause)
                            
    def printEvent(theEvent):
        string = theEvent.date.value
        if theEvent.place != "":
            string += " in "+theEvent.place
        return string

    def updateIfChanged(theEvent, otherEvent, changed):
        if (theEvent.date.updateIfChanged(otherEvent.date, changed)) | (theEvent.place != otherEvent.place) | (theEvent.cause != otherEvent.cause):
            changed = True
        theEvent.place = otherEvent.place
        theEvent.cause = otherEvent.cause
        return changed
    
###############################################################################
# date
###############################################################################
class date:
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    days = [31,29,31,30,31,30,31,31,30,31,30,31]    # don't worry about leap years
    modifiers = ["FROM", "TO", "ABT", "BEF", "AFT", "BET"]
    
    def __init__(self, value):
        # dates are initialized with whatever string was specified
        self.value = value
        self.year = ""
        self.month = ""
        self.day = ""
    
    def isValid(self):
        # parse into the components, but don't validate yet
        if (self.value == "") | (self.value == "unknown"):
            self.year = self.value
        else:
            values = self.value.translate(string.maketrans("-/", "  ")).split() # allow various delimiters
            if len(values) == 3:
                if values[0].isdigit(): # dd mmm yyyy
                    self.day = values[0]
                    self.month = values[1]
                else:                   # mmm dd yyyy
                    self.month = values[0]
                    self.day = values[1]
                self.year = values[2]
            elif len(values) == 2:      # mmm yyyy
                if values[0] == "ABT":
                    self.year = values[1]
                elif values[0] == "BEF":
                    self.year = values[1]
                else:
                    self.month = values[0]
                    self.year = values[1]
            else:                       # yyyy
                self.year = values[0]
        self.month = self.month.capitalize()[0:3]
        if debug: print "date:", self.value, "-->", self.day, self.month, self.year

        # now validate
        if self.year != "":
            if not self.year.isdigit(): return False
            if len(self.year) != 4: return False
            if self.month != "":
                try:
                    monthIndex = self.months.index(self.month)
                except: return False
                if self.day != "":
                    try:
                        if int(self.day) > self.days[monthIndex]: return False
                        elif int(self.day) <= 0: return False
                    except: return False
        return True

    def normalize(self):
        # replace the value with the normalized format "dd mmm yyyy"
        self.value = self.year
        if self.month != "":
            self.value = self.month+" "+self.value
        if self.day != "":
            self.value = self.day+" "+self.value
        return self.value

    def numeric(self):
        # return a sortable numeric date yyyymmdd
        value = self.year
        if self.month != "":
            value += "%2d" % self.months.index(self.month)
        if self.day != "":
            value += "%2d" % int(self.day)
        return value
            
#    def printDate(theDate):
#        string = theDate.year
#        if theDate.month != "":
#            string = theDate.month+" "+string
#        if theDate.day != "":
#            string = theDate.day+" "+string
#        return string

    def updateIfChanged(theDate, otherDate, changed):
        if (theDate.value != otherDate.value):
            changed = True
        theDate.value = otherDate.value
        return changed
        
###############################################################################
# note
###############################################################################
class note:
    def __init__(theNote, value=""):
        if debug: print "note:"
        theNote.value = value

    def readNote(theNote, theFile, lastLevel):
        if debug: print "readNote:", lastLevel
        theFile.readLine()
        while theFile.level > lastLevel:
            if theFile.tag == "CONT":
                theNote.value += "\n"+theFile.value
            else:
                print "Unrecognized note tag", theFile.tag            
            theFile.readLine()

    def printNote(theNote):
        string = ""
        for chunk in theNote.value.split("\n"):
            string += chunk+"<br>"
        return string
        
    def writeNote(theNote, theFile, level):
        if debug: print "writeNote:", level
        tag = "NOTE"
        for chunk in theNote.value.split("\n"):
            theFile.writeLine(level, tag, chunk)
            if tag == "NOTE":
                tag = "CONT"
                level += 1

    def updateIfChanged(theNote, otherNote, changed):
        if theNote.value != otherNote.value:
            theNote.value = otherNote.value
            return True
        else:
            return changed

###############################################################################
# image
###############################################################################
class image:
    def __init__(self, theType="", theFileName="", theTitle=""):
        self.type = theType
        self.fileName = theFileName
        self.title = theTitle

    def readImage(self, theFile, lastLevel):
        theFile.readLine()
        while theFile.level > lastLevel:
            if theFile.tag == "FORM":
                self.type = theFile.value
            elif theFile.tag == "FILE":
                self.fileName = theFile.value
            elif theFile.tag == "TITL":
                self.title = theFile.value
            else:
                print "Unrecognized image tag", theFile.tag            
            theFile.readLine()
        
    def writeImage(self, theFile, level):
        theFile.writeLine(level, "OBJE")
        level += 1
        if self.type != "":
            theFile.writeLine(level, "FORM", self.type)
        if self.fileName != "":
            theFile.writeLine(level, "FILE", self.fileName)
        if self.title != "":
            theFile.writeLine(level, "TITL", self.title)



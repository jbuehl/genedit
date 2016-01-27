#!/usr/bin/python

import cgi, cgitb, sys, time, os, Cookie
from genconf import *
from genenv import *
from genclasses import *
from genutils import *

###############################################################################
# display functions
###############################################################################

def displayPerson(theContext):
    (persons, families, outFile, logFile, form, thePerson, function, functionIndex, userName) = theContext.getValues()
    if thePerson.id == "I000":  # person zero means display the list of people
        displayPeople()
        return
        
    outFile.printHtmlHeader(thePerson.name+" "+thePerson.surname)
    if debugForm: print form
    outFile.write("<h1>"+thePerson.name+" "+thePerson.surname+"</h1>")
    outFile.write('<form name="display" action="'+scriptName+'" method="get">')
    displayButtons(outFile, thePerson, form.getfirst("lastid", "I000"), userName)
    displayAttributes(outFile, thePerson)
    displayFamilyChild(outFile, thePerson, persons, families)
    for spouseIndex in range(len(thePerson.familySpouse)):
        displayFamilySpouse(outFile, thePerson, spouseIndex, persons, families)
    displayNotes(outFile, thePerson)
    for theImage in thePerson.images:
        displayImage(outFile, theImage)
    outFile.write("</form>")

def displayButtons(outFile, thePerson, lastId, userName):
#    if userName == "":
#        disabled = "disabled"
#    else:
#        disabled = ""
    disabled = ""
    outFile.write('<input type="submit" name="function" value="'+peopleFunction+'" />')
    outFile.write('<input type="submit" name="function" value="'+descendantsFunction+'" />')
    outFile.write('<input type="submit" name="function" value="'+ancestorsFunction+'" />')
    outFile.write('<input type="submit" name="function" value="'+editFunction+'" '+disabled+' />')
    outFile.write('<input type="hidden" name="id" value="'+thePerson.id+'"/>')
    outFile.write('<input type="hidden" name="lastid" value="'+lastId+'"/>')
    outFile.write("<font size=1>"+thePerson.id+"</font>")
    outFile.write("<br><br>")

def displayAttributes(outFile, thePerson):
    outFile.write("Born: "+thePerson.birth.printEvent()+"<br>")
    if thePerson.death.date.value != "":
        outFile.write("Died: "+thePerson.death.printEvent())
        if thePerson.death.cause != "":
            outFile.write(" Cause: "+thePerson.death.cause)
        outFile.write("<br>")
    if thePerson.occupation is not "":
        outFile.write("Occupation: "+thePerson.occupation+"<br>")
  	    
def displayFamilyChild(outFile, thePerson, persons, families):
    if thePerson.familyChild != "":
        if families[thePerson.familyChild].husband != "":
            outFile.write("Father: "+persons[families[thePerson.familyChild].husband].printPersonBrief(urlPath, thePerson.id))
            outFile.write("<br>")
        if families[thePerson.familyChild].wife != "":
            outFile.write("Mother: "+persons[families[thePerson.familyChild].wife].printPersonBrief(urlPath, thePerson.id))
            outFile.write("<br>")
        outFile.write("<br>")

def displayFamilySpouse(outFile, thePerson, spouseIndex, persons, families):
    familySpouse = thePerson.familySpouse[spouseIndex]
    if len(thePerson.familySpouse) == 1:
        spouseDisp = ""
    else:
        spouseDisp = (" %d" % (spouseIndex+1))
    if thePerson.sex == "M":
        if families[familySpouse].wife != "":
            outFile.write("Wife"+spouseDisp+": "+persons[families[familySpouse].wife].printPersonBrief(urlPath, thePerson.id))
        else:
            outFile.write("Wife"+spouseDisp+": "+" unknown")
    else:
        if families[familySpouse].husband != "":
            outFile.write("Husband"+spouseDisp+": "+persons[families[familySpouse].husband].printPersonBrief(urlPath, thePerson.id))
        else:
            outFile.write("Husband"+spouseDisp+": "+" unknown")
    outFile.write("<ul>")
    if families[familySpouse].marriage.date.year != "":
        outFile.write("Married: "+families[familySpouse].marriage.printEvent()+"<br>")
    if families[familySpouse].note.value != "":
        outFile.write("<br><li>Notes:</li><br>"+families[familySpouse].note.value+"<br>")
    if families[familySpouse].children != []:
        outFile.write("Children: <ul>")
        for child in families[familySpouse].children:
            outFile.write(""+persons[child].printPersonBrief(urlPath, thePerson.id))
            outFile.write("<br>")
        outFile.write("</ul>")
    outFile.write("</ul>")

def displayNotes(outFile, thePerson):
    if thePerson.note.value != "":
        outFile.write("<br>Notes:<br>"+thePerson.note.printNote()+"<br>")

def displayImage(outFile, theImage):
    outFile.write('<p align="left">')
    outFile.write('<img src="http://'+domain+'/'+imagePath+theImage.fileName+'" /><br><br>')
    outFile.write(theImage.title+"<br><br>")

def displayPeople(theContext):
    (persons, families, outFile, logFile, form, thePerson, function, functionIndex, userName) = theContext.getValues()
    outFile.printHtmlHeader("People")
    if debugForm: print form
    outFile.write("<h1>People</h1>")
    outFile.write("<table border=1 width=768 style='table-layout:fixed'>")
    outFile.write("<col width=480><col width=144><col width=144>")
    outFile.write("<tr>")
    outFile.write("<th>Name</th>")
    outFile.write("<th>Birth</th>")
    outFile.write("<th>Death</th>")
    outFile.write("</tr>")
    personList = []
    fileNames = os.listdir(filePath)
    for fileName in fileNames:
        if fileName[0:1] == "I":
            thePerson = person(fileName.split(".")[0])
            thePerson.readPersonFromFile()
            persons[thePerson.id] = (thePerson)
            name = thePerson.surname+", "+thePerson.name
            personList.append((name, thePerson.id))
    personList.sort()
    for line in personList:
        name = line[0]
        id = line[1]
        birth = persons[id].birth.date.value
        if persons[id].death is not None:
            death = persons[id].death.date.value
        else:
            death = ""
        outFile.write("<tr><td>"+persons[id].printPersonLink(urlPath, "Display", "I000"))
        outFile.write("</td>")
        outFile.write("<td>"+birth+"</td>")
        outFile.write("<td>"+death+"</td>")
        outFile.write("</tr>")
    outFile.write("</table>")

def displayDescendants(theContext):
    (persons, families, outFile, logFile, form, thePerson, function, functionIndex, userName) = theContext.getValues()
    outFile.printHtmlHeader("Descendants")
    if debugForm: print form
    lastId = form.getfirst("lastid", "I000")
    readAllPersons(persons)
    readAllFamilies(families)
    outFile.write("<h1>Descendants of "+thePerson.name+" "+thePerson.surname+"</h1>")
    outFile.write('<form name="edit" action="'+scriptName+'" method="get">')
    outFile.write('<input type="submit" name="function" value="People" />')
    outFile.write('<input type="submit" name="function" value="Display" />')
    outFile.write('<input type="submit" name="function" value="Ancestors" />')
    outFile.write('<input type="submit" name="function" value="Edit" />')
    outFile.write('<input type="hidden" name="id" value="'+thePerson.id+'"/>')
    outFile.write('<input type="hidden" name="lastid" value="'+lastId+'"/>')
    outFile.write("<font size=1>"+thePerson.id+"</font>")
    outFile.write("</form>")
    outFile.write('<font size="2" face="courier" color="black">')
    displayDescendant(outFile, thePerson, 1, persons, families)
    outFile.write('</font>')
    
def displayDescendant(outFile, thePerson, level, persons, families):
    outFile.write(thePerson.printPersonIndent(urlPath, level, str(level), "----")+"<br>")
    if thePerson.familySpouse is not []:
        for family in thePerson.familySpouse:
            if thePerson.sex == "M":
                spouse = families[family].wife
            else:
                spouse = families[family].husband
            if spouse != "":
                theSpouse = persons[spouse]
                outFile.write(theSpouse.printPersonIndent(urlPath, level, "+", "----")+"<br>")
            if families[family].children != []:
                for child in families[family].children:
                    displayDescendant(outFile, persons[child], level+1, persons, families)

def displayAncestors(theContext):
    (persons, families, outFile, logFile, form, thePerson, function, functionIndex, userName) = theContext.getValues()
    outFile.printHtmlHeader("Ancestors")
    if debugForm: print form
    lastId = form.getfirst("lastid", "I000")
    readAllPersons(persons)
    readAllFamilies(families)
    outFile.write("<h1>Ancestors of "+thePerson.name+" "+thePerson.surname+"</h1>")
    outFile.write('<form name="edit" action="'+scriptName+'" method="get">')
    outFile.write('<input type="submit" name="function" value="People" />')
    outFile.write('<input type="submit" name="function" value="Descendants" />')
    outFile.write('<input type="submit" name="function" value="Display" />')
    outFile.write('<input type="submit" name="function" value="Edit" />')
    outFile.write('<input type="hidden" name="id" value="'+thePerson.id+'"/>')
    outFile.write('<input type="hidden" name="lastid" value="'+lastId+'"/>')
    outFile.write("<font size=1>"+thePerson.id+"</font>")
    outFile.write("</form>")
    outFile.write('<font size="2" face="courier" color="black">')
    ancestors = []
    displayAncestor(outFile, thePerson, ancestors, 1, persons, families)
    ancestors.reverse()
    for ancestor in ancestors:
        outFile.write(ancestor)
    outFile.write('</font>')

def displayAncestor(outFile, thePerson, ancestors, level, persons, families):
    ancestors.append(thePerson.printPersonIndent(urlPath, level, str(level), "====")+"<br>")
    if thePerson.familyChild != "":
        if families[thePerson.familyChild].husband != "":
            theFather = persons[families[thePerson.familyChild].husband]
            displayAncestor(outFile, theFather, ancestors, level+1, persons, families)
        if families[thePerson.familyChild].wife != "":
            theMother = persons[families[thePerson.familyChild].wife]
            displayAncestor(outFile, theMother, ancestors, level+1, persons, families)


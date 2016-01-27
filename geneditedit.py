#!/usr/bin/python

import cgi, cgitb, sys, time, os, Cookie
from genconf import *
from genenv import *
from genclasses import *

###############################################################################
# edit functions
###############################################################################

def editPerson(theContext, errorMsg=""):
    (persons, families, outFile, logFile, form, thePerson, function, functionIndex, userName) = theContext.getValues()
    if thePerson.id == "I000":  # person zero means display the list of people
        displayPeople()
        return

    if userName in adminUsers:
        disabled = ""
    else:
        disabled = "disabled"
        
    outFile.printHtmlHeader(thePerson.name+" "+thePerson.surname)
    if debugForm: print form
    outFile.write("<h1>"+thePerson.name+" "+thePerson.surname+"</h1>")
    if errorMsg != "":
        outFile.write('<font color="red">Errors:<br>'+errorMsg+'</font>')
    outFile.write('<form name="update" enctype="multipart/form-data" action="'+scriptName+'" method="post">')
    editButtons(outFile, thePerson, disabled, form.getfirst("lastid", "I000"))
    editAttributes(outFile, thePerson, disabled)
    editFamilyChild(outFile, thePerson, disabled, persons, families)
    outFile.write('<input type="hidden" name="spouses" value="'+str(len(thePerson.familySpouse))+'"/>')
    for spouseIndex in range(len(thePerson.familySpouse)):
        editFamilySpouse(outFile, thePerson, persons, families, spouseIndex, disabled)
    editNotes(outFile, thePerson, disabled)
    editImages(outFile, thePerson, disabled)
    outFile.write('</form>')
    outFile.write('<br>')

def editButtons(outFile, thePerson, disabled, lastId):
    outFile.write('<input type="submit" name="function" value="'+peopleFunction+'" />')
    outFile.write('<input type="submit" name="function" value="'+descendantsFunction+'" />')
    outFile.write('<input type="submit" name="function" value="'+ancestorsFunction+'" />')
    outFile.write('<input type="submit" name="function" value="'+displayFunction+'" /> ')
    outFile.write('<font size=1>'+thePerson.id+'</font>')
    outFile.write('<br>')
    outFile.write('<input type="submit" name="function" value="'+updateFunction+'" /> ')
    outFile.write('<input type="submit" name="function" value="'+deleteFunction+'" '+disabled+'/> ')
    outFile.write('<input type="submit" name="function" value="'+addFamilyFunction+'" />')
    if thePerson.note.value == "":
        outFile.write('<input type="submit" name="function" value="'+addNotesFunction+'" />')
    outFile.write('<br><br>')
    outFile.write('<input type="hidden" name="id" value="'+thePerson.id+'"/>')
    outFile.write('<input type="hidden" name="lastid" value="'+lastId+'"/>')

def editAttributes(outFile, thePerson, disabled):
    outFile.write("Name: ")
    editName(outFile, thePerson, thePerson.name, thePerson.surname, thePerson.sex)
    outFile.write("<br>")
    outFile.write('Born: <input type="text" name="birthdate" value="'+thePerson.birth.date.value+'"/>')
    outFile.write(' Place: <input type="text" name="birthplace" value="'+thePerson.birth.place+'"/><br>')
    outFile.write('Died: <input type="text" name="deathdate" value="'+thePerson.death.date.value+'"/>')
    outFile.write(' Place: <input type="text" name="deathplace" value="'+thePerson.death.place+'"/>')
    outFile.write(' Cause: <input type="text" name="deathcause" size=40 value="'+thePerson.death.cause+'"/><br>')
    outFile.write('Occupation: <input type="text" name="occupation" value="'+thePerson.occupation+'"/><br>')

def editFamilyChild(outFile, thePerson, disabled, persons, families):
    father = ""
    mother = ""
    if thePerson.familyChild is not "":
        outFile.write('<input type="hidden" name="famc" value="'+thePerson.familyChild+'"/>')
        father = families[thePerson.familyChild].husband
        mother = families[thePerson.familyChild].wife
    outFile.write("Father: ")
    if father != "":
        outFile.write(persons[father].printPersonLink(urlPath, "Edit", thePerson.id))
    else:
        editName(outFile, thePerson, "", "", "none", "father")
    outFile.write('<br>')
    outFile.write("Mother: ")           
    if mother != "":
        outFile.write(persons[mother].printPersonLink(urlPath, "Edit", thePerson.id))
    else:
        editName(outFile, thePerson, "", "", "none", "mother")
    outFile.write('<br><br>')

def editFamilySpouse(outFile, thePerson, persons, families, spouseIndex, disabled):
    familySpouse = thePerson.familySpouse[spouseIndex]
    outFile.write('<input type="hidden" name="fams'+str(spouseIndex)+'" value="'+familySpouse+'"/>')
    if len(thePerson.familySpouse) == 1:
        spouseDisp = ""
    else:
        spouseDisp = (" %d" % (spouseIndex+1))
    outFile.write("Family"+spouseDisp+":<br>")
    outFile.write('<input type="submit" name="functionS'+str(spouseIndex)+'" value="'+removeFunction+'" '+disabled+'/> ')
    if families[familySpouse].note.value == "":
        outFile.write('<input type="submit" name="function" value="'+addNotesFunction+'" />')
    outFile.write("<font size=1>"+familySpouse+"</font>")
    outFile.write("<ul>")
    if thePerson.sex == "M":
        outFile.write("Wife: ")
        if families[familySpouse].wife != "":
            outFile.write(persons[families[familySpouse].wife].printPersonLink(urlPath, "Edit", thePerson.id)+"<br>")
        else:
            editName(outFile, thePerson, "", "", "none", "spouse"+str(spouseIndex))
            outFile.write('<input type="submit" name="function" value="'+addSpouseFunction+'" /><br>')
        outFile.write("")
    else:
        outFile.write("Husband: ")
        if families[familySpouse].husband != "":
            outFile.write(persons[families[familySpouse].husband].printPersonLink(urlPath, "Edit", thePerson.id)+"<br>")
        else:
            editName(outFile, thePerson, "", "", "none", "spouse"+str(spouseIndex))
            outFile.write('<input type="submit" name="function" value="'+addSpouseFunction+'" /><br>')
        outFile.write("")
    outFile.write('Married: <input type="text" name="marriagedate'+str(spouseIndex)+'" value="'+families[familySpouse].marriage.date.value+'"/>')
    outFile.write(' Place: <input type="text" name="marriageplace'+str(spouseIndex)+'" value="'+families[familySpouse].marriage.place+'"/><br>')
    outFile.write("")
    if families[familySpouse].note.value != "":
        outFile.write('Notes: <br><textarea name="notes'+str(spouseIndex)+'" cols=80 rows=5 wrap=soft>'+families[familySpouse].note.value+'</textarea><br>')
    outFile.write("Children:")
    outFile.write("<ul>")
    if families[familySpouse].children != []:
        childNumber = 1
        for child in families[familySpouse].children:
            outFile.write(persons[child].printPersonLink(urlPath, "Edit", thePerson.id))
            outFile.write("<br>")
    if families[familySpouse].husband != "":
        childSurname = persons[families[familySpouse].husband].surname
    else:
        childSurname = ""
    outFile.write('<input type="submit" name="function" value="'+addChildFunction+'" />')
    editName(outFile, thePerson, "", childSurname, "", "child"+str(spouseIndex))
    outFile.write("<br>")
    outFile.write("</ul>")
    outFile.write("</ul>")
    
def editNotes(outFile, thePerson, disabled):
    if thePerson.note.value != "":
        outFile.write('Notes: <br><textarea name="notes" cols=80 rows=5 wrap=soft>'+thePerson.note.value+'</textarea><br>')

def editImages(outFile, thePerson, disabled):
    outFile.write("Add an image ")
    outFile.write('<input type="file" name="image" size="40">')
    outFile.write(' Title: <input type="text" name="imagetitle" size=40 /><br>')
    imageSeq = 1
    outFile.write('<input type="hidden" name="images" value="'+str(len(thePerson.images))+'"/>')
    for theImage in thePerson.images:
        editImage(outFile, theImage, imageSeq, disabled)
        imageSeq += 1

def editImage(outFile, theImage, imageSeq, disabled):
    outFile.write('<p align="left">')
    outFile.write('<input type="hidden" name="image'+str(imageSeq)+'" value="'+str(imageSeq)+'"/>')
    outFile.write('<img src="http://'+domain+'/'+imagePath+theImage.fileName+'" /><br><br>')
    outFile.write('<input type="text" name="imagetitle'+str(imageSeq)+'" value="'+theImage.title+'" />')
    outFile.write('<input type="submit" name="functionI'+str(imageSeq)+'" value="'+removeFunction+'" '+disabled+'/> ')

def editName(outFile, thePerson, name="", surname="", sex="", control=""):
    outFile.write('<input type="text" name="'+control+'name" value="'+name+'"/> ')
    outFile.write('<input type="text" name="'+control+'surname" value="'+surname+'"/> ')
    if sex != "none":    # none means don't show the radio buttons
        maleCheck = ""
        femaleCheck = ""
        if sex == "M":
            maleCheck = "checked"
        elif sex == "F":
            femaleCheck = "checked"
        outFile.write('<input type="radio" name="'+control+'sex" value="M" '+maleCheck+'/> Male ')
        outFile.write('<input type="radio" name="'+control+'sex" value="F" '+femaleCheck+'/> Female')
        

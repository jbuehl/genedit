#!/usr/bin/python

import cgi, cgitb, sys, time, os, Cookie
from genconf import *
from genenv import *
from genclasses import *
from genutils import *

class commitList():
    # lists of persons and families to be changed or deleted
    def __init__(self):
        self.personsChanged = []
        self.personsDeleted = []
        self.familiesChanged = []
        self.familiesDeleted = []
        
###############################################################################
# update functions
###############################################################################

def updatePerson(theContext, errorMsg=""):
    (persons, families, outFile, logFile, form, thePerson, function, functionIndex, userName) = theContext.getValues()

    commits = commitList()
    errorMsg = updateAttributes(form, thePerson, function, commits, persons, families, errorMsg)
    errorMsg = updateFamilyChild(form, thePerson, function, commits, persons, families, errorMsg)

    familyList = []    
    for spouseIndex in range(int(form.getfirst("spouses", "0"))):
        errorMsg = updateFamilySpouse(form, thePerson, function, functionIndex, spouseIndex, familyList, commits, persons, families, errorMsg)
    thePerson.familySpouse = sortSpouses(familyList, families)

    imageList = []
    for imageIndex in range(int(form.getfirst("images", "0"))):
        errorMsg = updateImage(form, thePerson, function, functionIndex, imageIndex, imageList, commits, errorMsg)
    thePerson.images = imageList
    
    theImage = form.getfirst("image", "")
    if theImage != "":
        errorMsg = createImage(form, theImage, thePerson, commits, errorMsg)

    if function == addFamilyFunction:
        errorMsg = createMarriage(form, thePerson, function, commits, persons, families, errorMsg)
#    elif function == addSpouseFunction:
#        errorMsg = createPerson(form, thePerson, function, commits, persons, families, errorMsg)
    elif function == addNotesFunction:
        thePerson.note.value = " "
    elif function == deleteFunction:
        errorMsg = deletePerson(form, thePerson, function, commits, persons, families, errorMsg)
        if errorMsg == "":  # if the delete was successful, go back to the person who we came from
            theContext.thePerson = persons[form.getfirst("lastid", "I000")]
            readRelatives(theContext.thePerson, theContext.persons, theContext.families)
            # lastId = ?
        
    if errorMsg == "":  # commit all the changes if there were no errors
        for aPerson in commits.personsChanged:
            aPerson.writePersonToFile(userName, logFile)
        for aPerson in commits.personsDeleted:
            aPerson.file.deleteFile(userName, logFile)
        for aFamily in commits.familiesChanged:
            aFamily.writeFamilyToFile(userName, logFile)
        for aFamily in commits.familiesDeleted:
            aFamily.file.deleteFile(userName, logFile)
    return errorMsg

def updateAttributes(form, thePerson, function, commits, persons, families, errorMsg):
    changed = False
    (thePerson.name, changed) = updateIfChanged(thePerson.name, form.getfirst("name", ""), changed)
    (thePerson.surname, changed) = updateIfChanged(thePerson.surname, form.getfirst("surname", ""), changed)
    (thePerson.sex, changed) = updateIfChanged(thePerson.sex, form.getfirst("sex", ""), changed)
    
    birthDate = date(form.getfirst("birthdate", ""))
    birthPlace = form.getfirst("birthplace", "")
    changed = thePerson.birth.updateIfChanged(event(birthDate, birthPlace), changed)
    if not thePerson.birth.date.isValid():
        errorMsg += "Birth date must be in the form 'dd mmm yyyy'<br>"
    else:
        if changed & (thePerson.familyChild != ""):
            # sort the children of this person's familyChild by birth date
            theFamily = families[thePerson.familyChild]
            theFamily.children = sortChildren(theFamily.children, persons)
            addToList(theFamily, commits.familiesChanged)
    
    deathDate = date(form.getfirst("deathdate", ""))
    deathPlace = form.getfirst("deathplace", "")
    deathCause = form.getfirst("deathcause", "")
    changed = thePerson.death.updateIfChanged(event(deathDate, deathPlace, deathCause), changed)
    if not thePerson.death.date.isValid():
        errorMsg += "Death date must be in the form 'dd mmm yyyy'<br>"
    
    (thePerson.occupation, changed) = updateIfChanged(thePerson.occupation, form.getfirst("occupation", ""), changed)
    changed = thePerson.note.updateIfChanged(note(form.getfirst("notes", "")), changed)
    if changed:
        addToList(thePerson, commits.personsChanged)
    return errorMsg
    
def updateFamilyChild(form, thePerson, function, commits, persons, families, errorMsg):
    newFather = False    
    father = form.getfirst("father", "")
    if father == "":    # the father wasn't previously specified
        fatherName = form.getfirst("fathername", "")
        fatherSurname = form.getfirst("fathersurname", "")
        if (fatherName != "") | (fatherSurname != ""):  # a name was specified so create a new person
            theFather= createPerson(fatherName, fatherSurname, "M")
            newFather = True
                    
    newMother = False
    mother = form.getfirst("mother", "")
    if mother == "":    # the mother wasn't previously specified
        motherName = form.getfirst("mothername", "")
        motherSurname = form.getfirst("mothersurname", "")
        if (motherName != "") | (motherSurname != ""):  # a name was specified so create a new person
            theMother= createPerson(motherName, motherSurname, "F")
            newMother = True

    familyChild = form.getfirst("famc", "")
    if (errorMsg == "") & (newFather | newMother):   # a parent was created that wasn't there before          
        if familyChild == "":   # create a new family
            theFamily = createFamily(familyChild)
            familyChild = theFamily.id
            theFamily.children = [thePerson.id]
            thePerson.familyChild = familyChild
            addToList(thePerson, commits.personsChanged)
            addToList(theFamily, commits.familiesChanged)
        else:
            theFamily = families[familyChild]
            theFamily.readFamilyFromFile()
            
        if newFather:
            theFamily.husband = father
            theFather.familySpouse.append(familyChild)
            addToList(theFather, commits.personsChanged)
        if newMother:
            theFamily.wife = mother
            theMother.familySpouse.append(familyChild)
            addToList(theMother, commits.personsChanged)
            
        addToList(theFamily, commits.familiesChanged)
    return errorMsg

def sortChildren(children, persons):
    sortList = []
    for childId in children:
        if not (childId in persons):
            theChild = person(childId)
            persons[childId] = (theChild)
            theChild.readPersonFromFile()
        sortList.append((persons[childId].birth.date.numeric(), childId))
    sortList.sort()
    childList = []
    for item in sortList:
        childList.append(item[1])
    return childList
        
def sortSpouses(spouses, families):
    sortList = []
    for spouseId in spouses:
        sortList.append((families[spouseId].marriage.date.numeric(), spouseId))
    sortList.sort()
    spouseList = []
    for item in sortList:
        spouseList.append(item[1])
    return spouseList
        
def updateFamilySpouse(form, thePerson, function, functionIndex, spouseIndex, familyList, commits, persons, families, errorMsg):
    theFamilySpouse = form.getfirst("fams"+str(spouseIndex))
    familyList.append(theFamilySpouse)
    theFamily = families[theFamilySpouse]
    changed = False
    if (function == removeSpouseFunction) & (functionIndex == spouseIndex):
        #print function
        errorMsg = deleteFamily(form, thePerson, function, functionIndex, familyList, commits, persons, families, errorMsg)
    elif function == addChildFunction:
        children = int(form.getfirst("children", "0"))
        childName = form.getfirst("child"+str(spouseIndex)+"name", "")
        childSurname = form.getfirst("child"+str(spouseIndex)+"surname", "")
        childSex = form.getfirst("child"+str(spouseIndex)+"sex", "")
        if childName != "":     # a first name was specified so create a new person
            theChild = createPerson(persons, childName, childSurname, childSex)
            theChild.familyChild = theFamilySpouse
            addToList(theChild, commits.personsChanged)
            theFamily.children.append(theChild.id)
            changed = True
    else:
        spouseName = form.getfirst("spouse"+str(spouseIndex)+"name", "")
        spouseSurname = form.getfirst("spouse"+str(spouseIndex)+"surname", "")
        if (spouseName != "") | (spouseSurname != ""):     # a name was specified so create a new person
            theSpouse = createPerson(persons, spouseName, spouseSurname)
            theSpouse.familySpouse = [theFamilySpouse]
            if thePerson.sex == "M":
                theFamily.wife = theSpouse.id
                theSpouse.sex = "F"
            else:
                theFamily.husband = theSpouse.id
                theSpouse.sex = "M"
            addToList(theSpouse, commits.personsChanged)
            changed = True

        marriageDate = date(form.getfirst("marriagedate"+str(spouseIndex), ""))
        marriagePlace = form.getfirst("marriageplace"+str(spouseIndex), "")
        changed = theFamily.marriage.updateIfChanged(event(marriageDate, marriagePlace), changed)
        if not theFamily.marriage.date.isValid():
            errorMsg += "Marriage date must be in the form 'dd mmm yyyy'<br>"
        else:
            if changed:
                addToList(thePerson, commits.personsChanged)      
    if changed:
        addToList(theFamily, commits.familiesChanged)
    return errorMsg  
        
def updateImage(form, thePerson, function, functionIndex, imageIndex, imageList, commits, errorMsg):
    theImage = thePerson.images[imageIndex]
    changed = False
    if function == "Remove image "+str(imageIndex+1):
        try:
            os.remove(imagePath+theImage.fileName)
        except:
            pass
        changed = True
    else:
        (theImage.title, changed) = updateIfChanged(theImage.title,  form.getfirst("imagetitle"+str(imageIndex+1), ""), changed)
        imageList.append(theImage)
    if changed:
        addToList(thePerson, commits.personsChanged)
    return errorMsg
    
def updateIfChanged(current, new, changed):
    # replace the current value with the new value and set the changed flag if they are different
    if current != new:
        changed = True
    return (new, changed)

def createPerson(persons, name="", surname="", sex=""):
    theId = getId("person")
    thePerson = person(theId, name, surname, sex)
    persons[theId] = (thePerson)
    return thePerson

def createFamily(families):
    theId = getId("family")
    theFamily = family(theId)
    families[theId] = (theFamily)
    return theFamily

def createMarriage(form, thePerson, function, commits, persons, families, errorMsg):
    theFamily = createFamily(families)
    if thePerson.sex == "M":
        theFamily.husband = thePerson.id
    elif thePerson.sex == "F":
        theFamily.wife = thePerson.id
    else:
        errorMsg += "The person's sex must be specified before adding a marriage<br>"
    if errorMsg == "":
        addToList(theFamily, commits.familiesChanged)
        thePerson.familySpouse.append(theFamily.id)
        addToList(thePerson, commits.personsChanged)
    return errorMsg

def createImage(form, theImage, thePerson, commits, errorMsg):
    imageTypes = {"jpeg":"jpg", "png":"png", "gif":"gif"}
    imageType = form["image"].type.split("/")[1]
    imageTitle = form.getfirst("imagetitle", "")
    if imageType in imageTypes:
        if thePerson.images != []:
            seq = int(thePerson.images[-1].fileName.split(".")[0].split("-")[1])+1
        else:
            seq = 1
        fileName = thePerson.id+"-"+str(seq)+"."+imageTypes[imageType]
        imageFile = open(uploadPath+fileName, "w")
        imageFile.write(theImage)
        imageFile.close()
        os.system("mogrify -resize 800x600 -background white -extent 800x600 -format "+imageTypes[imageType]+" -quality 75 -path "+imagePath+" "+uploadPath+fileName)
        thePerson.images.append(image(imageTypes[imageType], fileName, imageTitle))
        addToList(thePerson, commits.personsChanged)
    else:
        errorMsg += "Image type must be"
        for key in imageTypes.keys():
            errorMsg += " "+key+","
        errorMsg = errorMsg.strip(",")+"<br>"
    return errorMsg

###############################################################################
# delete functions
###############################################################################

def deletePerson(form, thePerson, function, commits, persons, families, errorMsg):
    # check for links first
    if (thePerson.familyChild != "") & (thePerson.familySpouse != []):
        errorMsg += "This person cannot be deleted if they are both a child and a spouse<br>"
    if errorMsg == "":
        if thePerson.familyChild != "": # they are a child
            theFamilyChild = families[thePerson.familyChild]
            del theFamilyChild.children[theFamilyChild.children.index(thePerson.id)]
            addToList(theFamilyChild, commits.familiesChanged)
        else:                           # they are a spouse
            for familySpouse in thePerson.familySpouse:
                theFamilySpouse = families[familySpouse]
                if theFamilySpouse.husband == thePerson.id:
                    theFamilySpouse.husband = ""
                else:   # theFamilySpouse.wife == thePerson.id:
                    theFamilySpouse.wife = ""
                addToList(theFamilySpouse, commits.familiesChanged)
        addToList(thePerson, commits.personsDeleted)
        del persons[thePerson.id]
        del thePerson
    return errorMsg
    
def deleteFamily(form, thePerson, function, functionIndex, familyList, commits, persons, families, errorMsg):
    theFamily = families[thePerson.familySpouse[functionIndex]]
    if thePerson.sex == "M":
        spouse = theFamily.wife
    else:
        spouse = theFamily.husband
    if spouse != "":
        errorMsg += "Spouse must be deleted or moved before the marriage can be removed<br>"
    if theFamily.children != []:
        errorMsg += "Children must be deleted or moved before the marriage can be removed<br>"
    if errorMsg == "":   # only delete it if there is no spouse or children
        addToList(thePerson, commits.personsChanged)
        addToList(theFamily, commits.familiesDeleted)
        familyList.pop()  
        del families[theFamily.id]
        del theFamily
    return errorMsg

def addToList(theItem, theList):
    # add an item to t list if it isn't already there
    if theItem not in theList:
        theList.append(theItem)
        
      

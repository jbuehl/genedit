#!/usr/bin/python

import cgi, cgitb, sys, time, os, Cookie
from genconf import *
from genenv import *
from genclasses import *

###############################################################################
# utility functions
###############################################################################

def readAllPersons(persons):
    fileNames = os.listdir(filePath)
    for fileName in fileNames:
        if fileName[0:1] == "I":
            thePerson = person(fileName.split(".")[0])
            thePerson.readPersonFromFile()
            persons[thePerson.id] = (thePerson)
  
def readAllFamilies(families):
    fileNames = os.listdir(filePath)
    for fileName in fileNames:
        if fileName[0:1] == "F":
            theFamily = family(fileName.split(".")[0])
            theFamily.readFamilyFromFile()
            families[theFamily.id] = (theFamily)
  
def readRelatives(thePerson, persons, families):
# read all the immediate relatives of the person
    if thePerson.familyChild is not "":
        theFamily = family(thePerson.familyChild)
        families[thePerson.familyChild] = (theFamily)
        theFamily.readFamilyFromFile()
        if theFamily.husband is not "":
            husband = person(theFamily.husband)
            persons[theFamily.husband] = (husband)
            husband.readPersonFromFile()
        if theFamily.wife is not "":
            wife = person(theFamily.wife)
            persons[theFamily.wife] = (wife)
            wife.readPersonFromFile()
    if thePerson.familySpouse is not []:
        for familySpouse in thePerson.familySpouse:
            theFamily = family(familySpouse)
            families[familySpouse] = (theFamily)
            theFamily.readFamilyFromFile()	            
            if thePerson.sex == "M":
                if theFamily.wife != "":
                    wife = person(theFamily.wife)
                    persons[theFamily.wife] = (wife)
                    wife.readPersonFromFile()
            else:
                if theFamily.husband != "":
                    	husband = person(theFamily.husband)
                    	persons[theFamily.husband] = (husband)
                    	husband.readPersonFromFile()
            if families[familySpouse].children != []:
                for childId in families[familySpouse].children:
            		child = person(childId)
            		persons[childId] = (child)
            		child.readPersonFromFile()
	
def getId(idType):
    # return the next available person or family identifier
    idFile = open(filePath+idType+".dat", "r")
    nextId = idFile.read().strip("\r").strip("\n")
    idFile.close()
    nextId = int(nextId)
    idFile = open(filePath+idType+".dat", "w")
    idFile.write("%3d" % (nextId + 1))
    idFile.close()
    if idType == "person":
        id = "I"+str(nextId)
    else:
        id = "F"+str(nextId)
    if debug: print "getId:", id
    return id



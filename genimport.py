#!/usr/bin/python

#  genimport.py
#  
#
#  Created by Joe Buehl on 9/8/11.
#  Copyright 2011 Buehl Technology. All rights reserved.

from genealogy import *
from genenv import *

if __name__ == "__main__":
    
    # parse the gedcom file into internal data
    
    fileName = "Glimn Buehl Tree 20110909.ged"
    theFile = gedcomFile(fileName)
    theFile.openFile()
    persons = {}
    families = {}
    theFile.readFile(persons, families)
    theFile.closeFile()
    del theFile

    # create the output files

    personId = "I000"
    familyId = "F000"
    
    for person in persons.keys():
        thePerson = persons[person]
        thePerson.file = gedcomFile(thePerson.id+".ged")
        thePerson.writePersonToFile("", "")
        if (thePerson.id != "unknown") & (thePerson.id > personId):
            personId = thePerson.id
        personIdFile = open(filePath+"person.dat", "w")
        personIdFile.write(str(int(personId[1:])+1))
        personIdFile.close()

    for family in families.keys():
        theFamily = families[family]
        theFamily.file = gedcomFile(theFamily.id+".ged")
        theFamily.writeFamilyToFile("", "")
        if (theFamily.id != "unknown") & (theFamily.id > familyId):
            familyId = theFamily.id
        familyIdFile = open(filePath+"family.dat", "w")
        familyIdFile.write(str(int(familyId[1:])+1))
        familyIdFile.close()


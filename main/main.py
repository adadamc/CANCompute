from distutils.log import error
import os
from tkinter import *
from tkinter import filedialog
import tkinter
from turtle import position  # sudo apt-get install python3-tk
import ocrmypdf
import tabula
import numpy as np
import fitz
import json
import re
from pathlib import Path

window = Tk()  # Making the GUI Window


def is_year(inputString):
    return bool(re.search(r'[1-2]{1}[0-9]{3}', inputString))

def is_word(inputString):
    return bool(re.search(r'[a-zA-Z]+', inputString))

def is_money(inputString):
    return bool(re.search(r'[0-9, -]+', inputString))

def has_num(inputString):
    inputString = re.sub('[\,\$\%\(\)\-\+ \.]', '', str(inputString))
    return bool(re.search(r'\d\n\d', inputString))

def noTextPage(paths, shortened=False):
    for p in paths:
        print("Path: ", p)

        jsondata = {}
        #jsondata['testKey'] = {}
        #jsondata['testKey']['class'] = "500"
        theYears = []
        currentTitle = ""
        lastLineYears = False # checking if the previous line had a year value
        oneYearFound = False # Do not start adding to json until a year has been found

        pt = Path(p)
        doc = fitz.open(p)
        j=0
        page_num = list(range(len(doc)))
        pagesSaved = 0

        for page in doc:
            a = page.get_text('blocks')
            count = 0
            
            for i in range(0, len(a) - 1):
                if(shortened==True):
                    yearsOnThisLine = False
                    theArr = a[i][4].split("\n")
                    amtOfNums = 0
                    unknownYears = 0

                    for z in theArr:
                        if is_year(z) or yearsOnThisLine == True:
                            print("Year value found: ", z)
                            if(lastLineYears == False):
                                theYears.clear()
                            theYears.append(z)
                            yearsOnThisLine = True
                            lastLineYears = True
                            oneYearFound = True
                        elif is_word(z):
                            print("Word value found: ", z)
                            currentTitle = z
                            amtOfNums = 0
                        elif oneYearFound == True and is_money(z):
                            print("Num value found: ", z)
                            if not (str(currentTitle) in jsondata):
                                jsondata[str(currentTitle)] = {}
                                print("Made key: ", str(currentTitle))

                            if(len(theYears) <= amtOfNums):
                                unknownYears = unknownYears + 1
                                jsondata[str(currentTitle)]['unknownYear' + str(unknownYears)] = str(z)
                            else:
                                if str(theYears[amtOfNums]) in jsondata[str(currentTitle)]:
                                    jsondata[str(currentTitle)][str(theYears[amtOfNums]) + "-" + str(amtOfNums)] = str(z)
                                    print("SAME KEY [APPENDED NUMBER TO KEY] Outer key: ", str(currentTitle), " with inner key: ", str(theYears[amtOfNums]), " with value: ", str(z))
                                else:
                                    jsondata[str(currentTitle)][str(theYears[amtOfNums])] = str(z)
                                    print("Outer key: ", str(currentTitle), " with inner key: ", str(theYears[amtOfNums]), " with value: ", str(z))
                            amtOfNums = amtOfNums + 1
                        else:
                            print("Unknown: ", z)
                    if(yearsOnThisLine == False):
                        lastLineYears = False
                if has_num(a[i][4]):
                    if count == 2:
                        page_num.remove(page.number)
                        pagesSaved = pagesSaved + 1
                        break
                    count += 1
        if shortened == False:
            doc.delete_pages(page_num)
        if pagesSaved > 0:
            if shortened == False:
                doc.save(str(p[:len(p)-4]) + "_Short.pdf")
                noTextPage([str(p[:len(p)-4]) + "_Short.pdf"], True)
        else:
            print("NOTICE:Could not find any pages that are believed to be financial documents")
        doc.close
        j+=1

        # Make json data

        if(shortened):
            json_string = json.dumps(jsondata)
            print(json_string)
            with open(str(p[:len(p)-4]) + ".json", 'w') as outfile:
                outfile.write(json_string)

    window.deiconify()  # Makes the GUI window visible

def makeFilesReadable(filePaths):
    validPaths = []  # Array of pdf files
    invalidFiles = []  # Array of non-pdf files
    conversions = 0  # Tracks amt of pdfs converted through ocrmypdf (readable format)
    for x in filePaths:
        if x.endswith(".pdf"):  # Check if each file is a .pdf
            validPaths.append(x)
        else:
            invalidFiles.append(x)
    for x in validPaths:
        if __name__ == '__main__':  # To ensure correct behavior on Windows and macOS
            try:
                ocrmypdf.ocr(x, x, deskew=True, force_ocr=True)
                print("Converted", x, "using ocrmypdf with a total of", conversions, "conversions.")
                conversions = conversions + 1
            except:
                print("The following file caused ocrmypdf to error (may already have readable text)", x)
        else:
            print("Was unable to convert a file: not __main__")
    print("\n")
    print("Finished converting pdf files to readable formats")
    print("Here are some statistics:")
    print("Valid (.pdf) files found:", len(validPaths))
    print("Invalid (not .pdf) files/folders found:", len(invalidFiles))
    print("Of the", len(validPaths),
          "valid files, the following number have been converted to have machine readable text through ocrmypdf:",
          conversions)
    print("Of the", len(validPaths), "valid files, the following had an error (may already have readable text):",
          (len(validPaths) - conversions))
    noTextPage(validPaths)

    
def selectFiles():
    path = filedialog.askopenfilenames(title="Select File(s)")
    if len(path) != 0:  # Did user select at least 1 file
        window.withdraw()  # Hides the GUI window
        makeFilesReadable(path)


def selectDirectory():
    path = filedialog.askdirectory(title="Select a Directory")
    if path != "":  # Did user select a folder (if not it should be an empty string)
        window.withdraw()  # Hides the GUI window
        folderContents = os.listdir(path)  # Array of all files in the folder
        for x in range(0, len(folderContents)):
            folderContents[x] = path + "/" + folderContents[x]  # Makes the path absolute instead of relative
        makeFilesReadable(folderContents)


# Show the menu once the code runs
def showMenu():
    window.geometry("400x100")
    window.title("CANCompute - File Selection")
    label = Label(window,
                  text="Extract info from PDF file(s) to json")  # Instructions telling user to select a file or directory
    label.pack()
    button = Button(text="Select Files",
                    command=selectFiles)  # Creats button for user to click after reading the instruction, when clicked selectDirOrFile will run
    button.pack()
    button.place(relx=0.35, rely=0.45, anchor=CENTER)
    button = Button(text="Select Folder",
                    command=selectDirectory)  # Creats button for user to click after reading the instruction, when clicked selectDirOrFile will run
    button.pack()
    button.place(relx=0.66, rely=0.45, anchor=CENTER)
    buttonClose = Button(text="Close",
                         command=window.destroy)  # Creats button for user to click after reading the instruction, when clicked selectDirOrFile will run
    buttonClose.pack()
    buttonClose.place(relx=0.5, rely=0.8, anchor=CENTER)
    window.mainloop()  # Keeps program running while waiting for user input


showMenu()  # Shows the initial menu
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
import re
from pathlib import Path

window = Tk()  # Making the GUI Window
def has_num(inputString):
    inputString = re.sub('[\,\$\%\(\)\-\+ \.]', '', str(inputString))
    return bool(re.search(r'\d\n\d', inputString))

def noTextPage(paths):
    for p in paths:
        pt = Path(p)
        doc = fitz.open(p)
        j=0
        page_num = list(range(len(doc)))

        for page in doc:
            a = page.get_text('blocks')
            count = 0
            for i in range(0, len(a) - 1):
                print("ai4:",a[i][4])
                if has_num(a[i][4]):
                    if count == 2:
                        page_num.remove(page.number)
                        break
                    count += 1
            print('fin')
        doc.delete_pages(page_num)
        doc.save(str(p[:len(p)-4]) + "_Short.pdf")
        doc.close
        j+=1
    window.deiconify()  # Makes the GUI window visible

def convertFile(paths):
    for x in range(0, len(paths)):
        df = tabula.read_pdf(paths[x], multiple_tables=True, pages='all',
                             guess=False)  # Converts PDF to put info in a DataFrame
        print("df: ", df)
        i = 1
        for t in df:
            print(i)
            t.to_csv('output' + str(i) + '.csv', encoding='utf-8')
            i += 1
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
                ocrmypdf.ocr(x, x, deskew=True, force_ocr=False)
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
    #convertFile(validPaths)
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
    window.title("File Selection")
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
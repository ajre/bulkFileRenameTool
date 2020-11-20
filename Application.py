from tkinter import *
import os
from FileManager import FileManager
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory
from tkinter import PhotoImage
from datetime import datetime 
from tkinter.ttk import Progressbar
from tkinter import messagebox
import re
 
class Application(Frame):
    """
    This Module launches the 'BULK FILE RENAME TOOL' application gui.
    Responsible for rendering the application UI and updating it. 

    """
    def __init__(self, root):
        """Method to call draw items on the tkinter window object"""
        self.root = root
        self.initialize_user_interface()

    def get_dir(self):
        """Method responsible for getting the directory path as well as filesname list in that directory"""
        path = askdirectory(title='Select Folder')
        if path == "":
            self.dirDispLabel['text'] = " Plz select a directory first."
        else:
            self.dirDispLabel['text'] = path
        self.dir = path
        self.filesList = self.fileManager.getDirFiles(self.dir)
        self.display_files()

    def clear(self, event):
        """Method responsible for selecting the text inside a entry widget whenever on focus"""
        event.widget.selection_range(0, END)

 
    def columnHeaderClicked(self, id):
        """
        Method responsible for sorting the filenames based on alphablet, date of creation and file size both ascending and descending order

        paramater:
        id (int): The clicked header index
        
        """
        files = []
        folder = []
        if id == 0:
            for entry in self.filesList:
                if entry[3] == 0:
                    files.append(entry)
                else:
                    folder.append(entry)
            # T1, T2, T3 -> Boolean varable to keep check on whether to sort files ascending or descending
            # filelist -> a list containing list of files in the current direcory [filename, filesize, dateof creation, isfile/isFolder]
            if self.T1 == True:
                files.sort(key=lambda x: x[0].lower())
                folder.sort(key=lambda x: x[0].lower())
                for f in folder:
                    files.insert(0, f)
                self.T1 = False
            else:
                files.sort(reverse=True,
                         key=lambda x: x[0].lower())
                folder.sort(reverse=True,
                         key=lambda x: x[0].lower())
                for f in folder:
                    files.insert(len(files), f)
                self.T1 = True
        elif id == 1:
            for entry in self.filesList:
                if entry[3] == 0:
                    files.append(entry)
                else:
                    folder.append(entry)
            if self.T2 == True:
                files.sort(key=lambda x: int(x[1].split(" ")[0]))
                files.sort(key=lambda x: int(x[1].split(" ")[0]))
                for f in folder:
                    files.insert(0, f)
                self.T2 = False
            else:
                files.sort(reverse=True, key=lambda x: int( x[1].split(" ")[0]) )
                files.sort(reverse=True, key=lambda x: int( x[1].split(" ")[0]) )
                for f in folder:
                    files.insert(len(f), f)
                self.T2 = True
        else:
            if self.T3 == True:
                files = self.filesList.sort(key=lambda date: datetime.strptime(date[2], '%d %b %Y'))
                self.T3 = False
            else:
                files = self.filesList.sort(reverse=True,
                                             key=lambda date: datetime.strptime(date[2], '%d %b %Y'))
                self.T3 = True
            self.display_files()
            return
        self.filesList = files
        self.display_files()

    def checkInput(self):
        """Method to check correct options are selected yet input fields are correct."""
        if len(self.filesList) <= 0:
            self.fileManager.display_error("Plz Select The Directory First")
            return 0
        # filemanager -> a FileManager object that takes care of all file related tasks and exceptions
        if self.fileManager.checkFilePermission(self.dir) == 0:
            self.fileManager.display_error("File read/write permission not allowed on the current directory")
            return 0

        if (self.check1.get() == 0) and (self.check2.get() == 0):
            self.fileManager.display_error("Plz Select < Enter Filename > or < Enter Regex > option")
            return 0

        if (self.check3.get() == 0) and (self.check4.get() == 0):
            self.fileManager.display_error("Plz Select < All File Types> or < Selected File Types > option")
            return 0

        self.userInputFileName = self.namingConventionInput2.get().strip()
        if self.fileManager.isValidFileName(self.userInputFileName) == 0:
            self.fileManager.display_error("Plz enter a valid file name.\n chars not allowed:'<', '>', '/', '\\', ':', '\"', '|', '\?', '*' ")
            return 0

        if self.check4.get() == 1:
            self.userInputFileTypes = self.fileTypesInput.get()
        
        if self.userInputFileName == "":
            self.fileManager.display_error("Plz enter a filename")
            return 0
        
        if self.check4.get() == 1:
            if self.userInputFileTypes == "":
                self.fileManager.display_error("Plz enter atleast one extention name like .png\n Supports multiple extentions seperated by comma: .png,.exe,.jpeg")
                return 0
        
        if self.check5.get() == 1:
            index = self.tree.selection()
            files = [self.tree.item(i)['values'] for i in index]
            if len(files) <= 1:
                self.fileManager.display_error("Plz Select atleast two items from the file list scrollview. \n Note: press ctrl and scroll to select multiple files.")
                return 0
            else:
                self.filesRenameList = files   

        if  self.check4.get() == 1:
            self.extentionList = self.fileManager.getExtentionList(self.userInputFileTypes)
            if len(self.extentionList) <= 0:
                    self.fileManager.display_error("None of the extentions specified in the textfield are valid.") 
                    return 0
        
        if self.check2.get() == 1:
            self.userInputRegexExp = self.namingConventionInput1.get().strip()
            if self.userInputRegexExp == "":
                self.fileManager.display_error("plz enter the regex expression to match file names")
                return 0
            elif self.fileManager.isValidRegex(self.userInputRegexExp) == 0:
                self.fileManager.display_error("Enter valid regex expression")
                return 0

        return 1

    def renameTask(self):
        """Method responsible for carrying out the rename task based on different combination of user input"""
        check1 = self.check1.get()
        check2 = self.check2.get()

        check3 = self.check3.get()
        check4 = self.check4.get()

        check5 = self.check5.get()

        if check1 == 1 and check3 == 1 and check5 == 1:    
            # rename using filename of all types and selected files only     
            zCnt = len(str(len(self.filesRenameList))) + 1 
            cnt = 1
            for item in self.filesRenameList:
                src = self.fileManager.combinePath(self.dir, item[0])
                filename, deli, extention = item[0].rpartition('.')
                filePart = self.fileManager.createCount(cnt, zCnt)
                newFileName = self.userInputFileName + filePart + "." + extention
                dst = self.fileManager.combinePath(self.dir, newFileName)
                self.fileManager.renameFile(src, dst)
                cnt += 1
            self.filesList = self.fileManager.getDirFiles(self.dir)
            self.display_files()
              
        elif check1 == 1 and check3 == 1 and check5 == 0:
            # rename using filename of all types on all files   
            fileList = self.fileManager.getDirFiles(self.dir)   
            zCnt = len( str(len(fileList)) ) + 1
            cnt = 1
            for item in fileList:
                src = self.fileManager.combinePath(self.dir, item[0])
                filename, deli, extention = item[0].rpartition('.')
                filePart = self.fileManager.createCount(cnt, zCnt)
                newFileName = self.userInputFileName + filePart + "." + extention
                dst = self.fileManager.combinePath(self.dir, newFileName)
                self.fileManager.renameFile(src, dst)
                cnt += 1
            self.filesList = self.fileManager.getDirFiles(self.dir)
            self.display_files()

        elif check1 == 1 and check4 == 1 and check5 == 1:
            # rename using filename of selected file types on selected files only
            fileListToRename = [] 
            for i, ele in enumerate(self.filesRenameList):
                filename, deli, extention = ele[0].rpartition('.')
                extention = "." + extention
                if extention in self.extentionList:
                    fileListToRename.append(self.filesRenameList[i])
            if len(fileListToRename) <= 0:
                self.fileManager.display_error("No matching file extention type found")
                return
            else:
                zCnt = len( str(len(fileListToRename)) ) + 1
                cnt = 1
                for item in fileListToRename:
                    src = self.fileManager.combinePath(self.dir, item[0])
                    filename, deli, extention = item[0].rpartition('.')
                    filePart = self.fileManager.createCount(cnt, zCnt)
                    newFileName = self.userInputFileName + filePart + "." + extention
                    dst = self.fileManager.combinePath(self.dir, newFileName)
                    self.fileManager.renameFile(src, dst)
                    cnt += 1
                self.filesList = self.fileManager.getDirFiles(self.dir)
                self.display_files()         

        elif check1 == 1 and check4 == 1 and check5 == 0:
            # rename using filename of selected file types on all files
            fileList = self.fileManager.getDirFiles(self.dir)  
            fileListToRename = []
            for i, ele in enumerate(fileList):
                filename, deli, extention = ele[0].rpartition('.')
                extention = "." + extention
                if extention in self.extentionList:
                    fileListToRename.append(fileList[i])
            if len(fileListToRename) <= 0:
                self.fileManager.display_error("No matching file extention type found")
                return
            else:
                zCnt = len( str(len(fileListToRename)) ) + 1
                cnt = 1
                for item in fileListToRename:
                    src = self.fileManager.combinePath(self.dir, item[0])
                    filename, deli, extention = item[0].rpartition('.')
                    filePart = self.fileManager.createCount(cnt, zCnt)
                    newFileName = self.userInputFileName + filePart + "." + extention
                    dst = self.fileManager.combinePath(self.dir, newFileName)
                    self.fileManager.renameFile(src, dst)
                    cnt += 1
                self.filesList = self.fileManager.getDirFiles(self.dir)
                self.display_files()

        elif check2 == 1 and check3 == 1 and check5 == 1:
            # rename using regex of all file types on selected files only            
            regex = self.userInputRegexExp   
            matchingFiles = []
            for i, ele in enumerate(self.filesRenameList):
                filename, deli, extention = ele[0].rpartition('.')
                if re.search(regex, filename):
                    matchingFiles.append(self.filesRenameList[i])
            if len(matchingFiles) <= 0:
                self.fileManager.display_error("No file name match the pattern")
                return
            zCnt = len( str(len(matchingFiles)) ) + 1
            cnt = 1
            for item in matchingFiles:
                src = self.fileManager.combinePath(self.dir, item[0])
                filename, deli, extention = item[0].rpartition('.')
                filePart = self.fileManager.createCount(cnt, zCnt)
                newFileName = self.userInputFileName + filePart + "." + extention
                dst = self.fileManager.combinePath(self.dir, newFileName)
                self.fileManager.renameFile(src, dst)
                cnt += 1
            self.filesList = self.fileManager.getDirFiles(self.dir)
            self.display_files()
             
        elif check2 == 1 and check3 == 1 and check5 == 0:
            # rename using regex of all file types  on all files
            regex = self.userInputRegexExp  
            matchingFiles = []
            fileList = self.fileManager.getDirFiles(self.dir)
            for i, ele in enumerate(fileList):
                filename, deli, extention = ele[0].rpartition('.')
                if re.search(regex, filename):
                    matchingFiles.append(fileList[i])
            if len(matchingFiles) <= 0:
                self.fileManager.display_error("No file name match the pattern")
                return
            zCnt = len( str(len(matchingFiles)) ) + 1
            cnt = 1
            for item in matchingFiles:
                src = self.fileManager.combinePath(self.dir, item[0])
                filename, deli, extention = item[0].rpartition('.')
                filePart = self.fileManager.createCount(cnt, zCnt)
                newFileName = self.userInputFileName + filePart + "." + extention
                dst = self.fileManager.combinePath(self.dir, newFileName)
                self.fileManager.renameFile(src, dst)
                cnt += 1
            self.filesList = self.fileManager.getDirFiles(self.dir)
            self.display_files()    

        elif check2 == 1 and check4 == 1 and check5 == 1:
            # rename using regex of selected file types on selected files
            regex = self.userInputRegexExp  
            matchingFiles = []
            for i, ele in enumerate(self.filesRenameList):
                filename, deli, extention = ele[0].rpartition('.')
                if re.search(regex, filename):
                    matchingFiles.append(self.filesRenameList[i])
            if len(matchingFiles) <= 0:
                self.fileManager.display_error("No file name match the pattern")
                return
            filteredList = []
            for i, ele in enumerate(matchingFiles):
                filename, deli, extention = ele[0].rpartition('.')
                extention = "." + extention
                if extention in self.extentionList:
                    filteredList.append(matchingFiles[i])
            if len(filteredList) <= 0:
                self.fileManager.display_error("Files that match to the pattern have no matching extentions")
                return
            zCnt = len( str(len(filteredList)) ) + 1
            cnt = 1
            for item in filteredList:
                src = self.fileManager.combinePath(self.dir, item[0])
                filename, deli, extention = item[0].rpartition('.')
                filePart = self.fileManager.createCount(cnt, zCnt)
                newFileName = self.userInputFileName + filePart + "." + extention
                dst = self.fileManager.combinePath(self.dir, newFileName)
                self.fileManager.renameFile(src, dst)
                cnt += 1
            self.filesList = self.fileManager.getDirFiles(self.dir)
            self.display_files()

        elif check2 == 1 and check4 == 1 and check5 == 0:
            # rename using regex of selected file types on all files
            regex = self.userInputRegexExp  
            matchingFiles = []
            fileList = self.fileManager.getDirFiles(self.dir)
            for i, ele in enumerate(fileList):
                filename, deli, extention = ele[0].rpartition('.')
                if re.search(regex, filename):
                    matchingFiles.append(fileList[i])
            if len(matchingFiles) <= 0:
                self.fileManager.display_error("No file name match the pattern")
                return
            filteredList = []
            for i, ele in enumerate(matchingFiles):
                filename, deli, extention = ele[0].rpartition('.')
                extention = "." + extention
                if extention in self.extentionList:
                    filteredList.append(matchingFiles[i])
            if len(filteredList) <= 0:
                self.fileManager.display_error("Files that match to the pattern have no matching extentions")
                return
            zCnt = len( str(len(filteredList)) ) + 1
            cnt = 1
            for item in filteredList:
                src = self.fileManager.combinePath(self.dir, item[0])
                filename, deli, extention = item[0].rpartition('.')
                filePart = self.fileManager.createCount(cnt, zCnt)
                newFileName = self.userInputFileName + filePart + "." + extention
                dst = self.fileManager.combinePath(self.dir, newFileName)
                self.fileManager.renameFile(src, dst)
                cnt += 1
            self.filesList = self.fileManager.getDirFiles(self.dir)
            self.display_files()
            

    def renameFiles(self):
        """This method responsible for checking user input as well as getting confirmation from user to proceed for rename task"""
        id = self.checkInput()
        if id == 0:
            return 
        else:
            msg = messagebox.askquestion ('Rename Files','Are you sure you want to rename the files.',icon = 'warning')
            if msg == 'yes':
                self.renameTask()
            else:
                return


    def sel(self, id):
        """Method responsible for handling changing user input choices"""
        if id == 0:
            self.regexbtn2.deselect()
            self.check2.set(0)
            self.namingConventionInput1.delete(0, END)
            self.namingConventionInput1['state'] = 'disabled'
            self.namingConventionInput2['state'] = 'normal'
            self.namingConventionInput2.delete(0, END)
            self.namingConventionInput2.insert(0, "enter filename here")

        elif id == 1:
            self.regexbtn1.deselect()
            self.check1.set(0)
            self.namingConventionInput1['state'] = 'normal'
            self.namingConventionInput2['state'] = 'normal'
            self.namingConventionInput1.delete(0, END)
            self.namingConventionInput1.insert(0, "enter regex exp here")
            self.namingConventionInput2.delete(0, END)
            self.namingConventionInput2.insert(0, "enter filename here")

        elif id == 2:
            self.selectedFilesBtn.deselect()
            self.check4.set(0)
            self.fileTypesInput.delete(0, END)
            self.fileTypesInput['state'] = 'disabled'

        else:
            self.allFilesBtn.deselect()
            self.check3.set(0)
            self.fileTypesInput['state'] = 'normal'
            self.fileTypesInput.delete(0,END)
            self.fileTypesInput.insert(0, " Enter extentions here: .png, .jpeg, .py")
       
    def initialize_user_interface(self):
        """Method responsible for drawing and postitioning widgets on the root window widget."""
        self.bgTheme1 = "#33333D"
        self.bgTheme2 = "#373740"
        self.btnFgColor = "#b7b2b2"
        self.btnBgColor = "#33333D"
        self.labelFgColor = "#e5dede"  
        self.labelBgColor = self.bgTheme2
        self.off_color = "red"
        self.on_color = "green"
        self.root.title("Bulk File Rename Tool")
        self.root.geometry("700x720")
        self.root.configure(background = self.bgTheme1)
        self.root.option_add("*Font", "helvetica 10 bold")
        self.root.resizable(False, False)  
        self.fileManager = FileManager()
        
        self.check1 = IntVar()
        self.check2 = IntVar()
        self.check3 = IntVar()
        self.check4 = IntVar()
        self.check5 = IntVar()

        self.T1 = True
        self.T2 = True
        self.T3 = True

        self.userInput1 = ""
        self.userInput2 = ""

        self.topFrame = LabelFrame(self.root, width = 700, height = 170, borderwidth = 0.4, relief = "raised")
        self.midFrame = LabelFrame(self.root, width = 700, height = 330, borderwidth = 0.4, relief = "raised")
        self.endFrame = LabelFrame(self.root, width = 700, height = 250, borderwidth = 0.4, relief = "raised")

        for i, frame in enumerate([self.topFrame, self.midFrame, self.endFrame]):
            if i == 0:
                frame.pack(expand=True, fill='both', padx = 15, pady = (10, 0))
            elif i == 1:
                frame.pack(expand=True, fill='both', padx = 15, pady = (10, 10))
            else:
                frame.pack(expand=True, fill='both', padx = 15, pady = (0, 10))
            frame.pack_propagate(0)
            frame.configure(background = self.bgTheme2)

        self.openDirectoryBtn = Button(self.topFrame, text = "Select Directory", bg = self.btnBgColor, fg = self.btnFgColor, borderwidth = 0.5, relief="raised", command = self.get_dir, width = 20, height = 2)
        self.openDirectoryBtn.place(x = 250, y = 8)

        self.l = Label(self.topFrame, text = "Dir: ", fg = self.labelFgColor, bg = self.labelBgColor, justify = "left", font = ("helvetica 10 bold"))
        self.l.place(x = 20, y = 59)

        self.dirDispLabel = Label(self.topFrame, text = os.getcwd(), fg = self.labelFgColor, bg = self.labelBgColor, justify = "left", font = ("helvetica 10 bold"))
        self.dirDispLabel.place(x = 50, y = 59)

        self.regexbtn1 = Checkbutton(self.topFrame, text = "Specify filename to rename\n files from directory", onvalue = 1, offvalue = 0, variable = self.check1, command = lambda: self.sel(0), fg = "green", bg = self.labelBgColor, justify = "left", font = ("helvetica 13 bold"), bd = 0, highlightthickness = 0)
        self.regexbtn1.place(x = 20, y = 84)
        self.regexbtn1.deselect()

        self.regexbtn2 = Checkbutton(self.topFrame, text = "Use Regex Exp to sort select files from dir", onvalue = 1, offvalue = 0, variable = self.check2, command = lambda: self.sel(1), fg = "green", bg = self.labelBgColor, justify = "left", font = ("helvetica 13 bold"))
        self.regexbtn2.place(x = 300, y = 93)
        self.regexbtn2.deselect()

        self.namingConventionInput1 = Entry(self.topFrame, fg = self.labelFgColor, state = "disabled", bg = self.labelBgColor, justify = "left", font = ("helvetica 13 bold"), border = 0.7, width = 25)
        self.namingConventionInput1.insert(0, "enter regex exp")
        self.namingConventionInput1.place(x = 25, y = 140)
        self.namingConventionInput1.bind("<FocusIn>", self.clear)

        self.namingConventionInput2 = Entry(self.topFrame, fg = self.labelFgColor, state = "disabled", bg = self.labelBgColor, justify = "left", font = ("helvetica 13 bold"), border = 0.7, width = 25)
        self.namingConventionInput2.insert(0, "enter file rename name")
        self.namingConventionInput2.place(x = 304, y = 140)
        self.namingConventionInput2.bind("<FocusIn>", self.clear)

        self.style1 = ttk.Style()
        self.style1.configure("Custom.Treeview.Heading",
            background="green", foreground="black", relief="flat")
        self.style1.map("Custom.Treeview.Heading",
            relief=[('active','groove'),('pressed','sunken')])

        self.tree = ttk.Treeview(self.midFrame, style = "Custom.Treeview", height = 330)
        self.tree.pack()

        self.vsb = ttk.Scrollbar(self.midFrame, orient="vertical", command=self.tree.yview)
        self.vsb.place(x=654, y=0, height=330)
        self.tree.configure(yscrollcommand=self.vsb.set)

        self.tree['columns'] = ("FileName", "FileSize", "FileCreated")
        self.tree.column("#0",width = 0, stretch = NO)

        self.icon = PhotoImage('sort_icon.png')

        self.tree.column("FileName", width = 300, anchor = W)
        self.tree.column("FileSize", width = 150, anchor = CENTER)
        self.tree.column("FileCreated", width = 250, anchor = CENTER)

        self.tree.heading("FileName", text = "File Name", anchor = CENTER, command = lambda: self.columnHeaderClicked(0))
        self.tree.heading("FileSize", text = "File Size", anchor = CENTER, command = lambda: self.columnHeaderClicked(1))
        self.tree.heading("FileCreated", text = "File Created", anchor = CENTER, command = lambda: self.columnHeaderClicked(2))

        self.allFilesBtn = Checkbutton(self.endFrame, text = "Include All Files Types", onvalue = 1, offvalue = 0, command = lambda: self.sel(2), variable = self.check3, fg = "green", bg = self.labelBgColor, justify = "left", font = ("helvetica 13 bold"))
        self.allFilesBtn.place(x = 20, y = 8)
        self.allFilesBtn.select()
        self.check3.set(1)

        self.selectedFilesBtn = Checkbutton(self.endFrame, text = "Rename Selected File Types Only", onvalue = 1, offvalue = 0, command = lambda: self.sel(3), variable = self.check4, fg = "green", bg = self.labelBgColor, justify = "left", font = ("helvetica 13 bold"))
        self.selectedFilesBtn.place(x = 290, y = 8)
        self.selectedFilesBtn.deselect()

        self.fileTypesLabel = Label(self.endFrame, text = "Enter ' , ' seperated extentions names: ", fg = self.labelFgColor, bg = self.labelBgColor, justify = "left", font = ("helvetica 10 bold"))
        self.fileTypesLabel.place(x = 20, y = 50)

        self.fileTypesInput = Entry(self.endFrame, fg = self.labelFgColor, state = "disabled", bg = self.labelBgColor, justify = "left", font = ("helvetica 13 bold"), border = 0.7, width = 35)
        self.fileTypesInput.place(x = 296, y = 50)
        self.fileTypesInput.insert(0, "eg: .exe,.png,.jpeg")
        self.fileTypesInput.bind("<FocusIn>", self.clear)

        self.renameSelectedFilesOption =  Checkbutton(self.endFrame, text = " <ctrl + click> to select files\n check this option to \n perform rename operation on selected files only ", onvalue = 1, offvalue = 0, variable = self.check5, fg = "green", bg = self.labelBgColor, justify = "left", font = ("helvetica 13 bold"))
        self.renameSelectedFilesOption.place(x = 20, y = 114)
        self.renameSelectedFilesOption.deselect()
        self.check5.set(0)

        self.renameAllFilesBtn = Button(self.endFrame, text = "Rename Files", command = self.renameFiles, bg = self.btnBgColor, fg = self.btnFgColor, borderwidth = 0.5, relief="raised", width = 30, height = 2)
        self.renameAllFilesBtn.place(x = 335, y = 100)

        self.style2 = ttk.Style()
        self.style2.configure("black.Horizontal.TProgressbar", background='green')


        self.root.bind_all("<Button-1>", lambda event:event.widget.focus_set())

        self.dir = os.getcwd()
        if self.fileManager.checkFilePermission(self.dir):
            self.filesList = self.fileManager.getDirFiles(self.dir)

        self.display_files()

    def display_files(self):
        """Method responsible for updating the items in the scrollable fileList"""
        for i in self.tree.get_children():
            self.tree.delete(i)
        if len(self.filesList) <= 0:
            return
        cnt = 0
        for file in self.filesList:
            self.tree.insert(parent='', index = 'end', iid = cnt, text = "", values = (file[0], file[1], file[2]))
            cnt += 1


if __name__ == '__main__':
    app = Application(Tk())
    app.root.mainloop()

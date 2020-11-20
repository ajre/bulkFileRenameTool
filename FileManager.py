import os
from datetime import datetime
from tkinter import messagebox as mbox
import sys
import re

class FileManager():

    def __init__(self):
        self.INVALID_CHAR = ['<', '>', '/', '\\', ':', '"', '|', '?', '*']
        self.RESERVED_FILENAMES = ['CON', 'PRN', 'AUX', 'NUL', "COM1", 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8',
        'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']

    def getDate(self, ctime):
        date = datetime.fromtimestamp(ctime).strftime('%d %b %Y')
        return date

    def getDirFiles(self, dir):
        self.path = dir
        try:
            self.allFiles = os.listdir(self.path)
        except:
            self.display_error("Directory Not Selected")
            return []
        fileList = []
        for file in self.allFiles:
            filePath = os.path.join(self.path, file)
            if os.path.isdir(filePath):
                pass
            else:
                size = round(os.path.getsize(filePath) / 1000)
                if size <= 0:
                    size = 0
                size = str(size) + ' kb'
                ctime = os.path.getctime(filePath)
                ctime = self.getDate(ctime)
                item = (file, size, ctime, 0)
                fileList.append(item)
        return fileList

    def display_error(self, msg, type = "Error"):
        mbox.showerror(type, msg)

    def checkFilePermission(self, path):
        if os.access(path, os.R_OK) and os.access(path, os.W_OK) and os.access(path, os.X_OK | os.W_OK):
            return 1
        else:
            return 0

    def isValidFileName(self, fileName):
        s = fileName.lstrip().rstrip()
        for item in self.RESERVED_FILENAMES:
            if item.lower() == s.lower():
                return 0
        res = [ele for ele in self.INVALID_CHAR if(ele in s)] 
        if bool(res) == True:
            return 0
        return 1

    def renameFile(self, source, dest):
        try:
            os.rename(source, dest)
            return 1
        except (FileExistsError):
            return 0

    def combinePath(self, path, filename):
        return os.path.join(path, filename)

        
    
    def getExtentionList(self, list):
        l = list.split(',')
        l1 = []
        for item in l:
            l1.insert(0, "f1" + item.strip())
        valid = []
        for e in l1:
            ex = e.lower()
            f, e = os.path.splitext(ex)
            print(f + ", " + e)
            if e == "":
                pass
            else:
                valid.insert(0, e)
        return valid

    def isValidRegex(self, regex):
        try:
            re.compile(regex)
            return 1
        except:
            return 0

    def createCount(self, num, zeros):
        zerosToAdd = zeros - len(str(num))
        numString = str(num)
        for i in range(zerosToAdd):
            numString = "0" + numString
        return numString

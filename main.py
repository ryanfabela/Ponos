import os
import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog
from fileHandler import handleFiles, createMischargesCSV
from receiptAnalyzer import ReceiptAnalyzer

DEFAULT_FOLDER_SELECTED_LABEL_TEXT = "No folder selected"

# Used to create GUI and handle button commands
# uses helper methods for handling files and analyzing the receipts
class App:
    def __init__(self, root):
        root.title("Ponos")
        width=600
        height=500
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
        root.configure(bg='#333333')

        FolderSelectButton=tk.Button(root)
        FolderSelectButton["bg"] = "#efefef"
        ft = tkFont.Font(family='Times',size=14)
        FolderSelectButton["font"] = ft
        FolderSelectButton["fg"] = "#000000"
        FolderSelectButton["justify"] = "center"
        FolderSelectButton["text"] = "Select Folder to review"
        FolderSelectButton.place(x=20,y=30,width=225,height=25)
        FolderSelectButton["command"] = self.FolderSelectButton_command

        self.FolderSelectedText = tk.Label(root)
        self.FolderSelectedText["text"] = DEFAULT_FOLDER_SELECTED_LABEL_TEXT
        self.FolderSelectedText["anchor"] = "w"
        self.FolderSelectedText["wraplength"] = "550"
        self.FolderSelectedText.place(x=20,y=60,width=550,height=50)                            

        self.GenerateReportButton=tk.Button(root)
        self.GenerateReportButton["bg"] = "#efefef"
        ft = tkFont.Font(family='Times',size=14)
        self.GenerateReportButton["font"] = ft
        self.GenerateReportButton["fg"] = "#000000"
        self.GenerateReportButton["justify"] = "center"
        self.GenerateReportButton["text"] = "Generate Report"
        self.GenerateReportButton.place(x=20,y=120,width=175,height=25)
        self.GenerateReportButton["command"] = self.GenerateReportButton_command
        self.GenerateReportButton["state"] = "disabled"

    # opens file explorer in current directory
    # asks user for folder to generate report from
    def FolderSelectButton_command(self):
      self.folderName = filedialog.askdirectory(initialdir = os.getcwd())
      
      if self.folderName: 
        self.FolderSelectedText.configure(text = "Folder Selected: " + self.folderName)
        self.GenerateReportButton["state"] = "normal"
      else:
        self.FolderSelectedText.configure(text = DEFAULT_FOLDER_SELECTED_LABEL_TEXT)
        self.GenerateReportButton["state"] = "disabled"

    # checks if file name has csv extension. If not, we append `.csv` to end
    def ensureSelectedFileIsCSV(self, file):
      defaultExtension = ".csv"
      originalFileName = file.name
      file.close()
      ensuredCSVFile = originalFileName if originalFileName[-len(defaultExtension):].lower() == defaultExtension else originalFileName + defaultExtension
      return ensuredCSVFile

    # takes folder and runs necessary helpers to get list of mischarges
    # then asks user where to save generated csv file
    def GenerateReportButton_command(self):
      directoryPath = self.folderName
      # get list of all files and product prices
      filesOutput = handleFiles(directoryPath)
      receiptChecker = ReceiptAnalyzer(filesOutput['products'])
      receipts = filesOutput['files']
      
      # go through all receipts in folder and validate their prices
      for receipt in receipts:
        receiptContent = receiptChecker.parseReceipt(receipt)
        receiptChecker.validatePrices(receiptContent)

      # sort from lowest total to highest
      sortedMischarges = sorted(receiptChecker.mischarges.values(), key=lambda x: x['total'], reverse=False)

      # ask user where they want the report saved and its name
      mischargesFile = filedialog.asksaveasfile(mode="w",filetypes=[("CSV Files","*.csv")], defaultextension=".csv")

      if mischargesFile is None:
        tk.messagebox.showerror(title="Invalid Report File", message="No file selected for report. Please try again")
        return None

      mischargesFile = self.ensureSelectedFileIsCSV(mischargesFile)

      createMischargesCSV(mischargesFile, sortedMischarges)
      tk.messagebox.showinfo(title="Finished", message="Report generated and saved to: " + mischargesFile)
      

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

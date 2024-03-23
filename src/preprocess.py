# take raw annotated data from ../data/raw
# do any cleaning steps necessary for spaCy to use it and save to ../data/processed

import os
import subprocess

class Preprocess:
    FILE_TYPE = "spacy"
    CONVERTER = "auto"
    
    def __init__(self, in_dir, out_dir, format):
        self.in_dir = in_dir
        self.out_dir = out_dir
        self.format = format
    
    # Checks for 'format' files in 'in_dir' 
    # returns list of files 
    def __check_dir__(self):
        files = []
        for file in os.listdir(self.in_dir):
            if file.endswith(self.format):
                files.append(file)
        return files

    # Runs the conversion command for each file in 'in_dir'
    def __run_conversion__(self):
        print()
        print("Converting: \n")

        base_command = "python3 -m spacy convert"
        command_list = []
        list_of_files = self.__check_dir__()

        for file in list_of_files:

            print("\t" + file)

            path = os.path.join(self.in_dir, file)
            command = base_command + f" {path} {self.out_dir} --converter {self.CONVERTER} --file-type {self.FILE_TYPE}"
            command_list.append(command)
        
        print() 
        
        for command in command_list:
            try:
                print(f"Running: {command} \n")
                os.system(command) 
                print()

            except Exception as e:
                print(e)
                continue
    
        print("Conversion Successful.\n")
    
    def run(self): 
        self.__run_conversion__()
# takes CoNLL-U formatted treebank from in_dir, converts to spaCy binary and saves to out_dir
# this must be done in order to train a spaCy component
# uses multithreading because executing commands one at a time kinda sucks...
import os
from concurrent.futures import ThreadPoolExecutor

class Conllu2Spacy:
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
        for root, _, filenames in os.walk(self.in_dir):
            for file in filenames:
                if file.endswith(self.format):
                    files.append(os.path.join(root, file))
        return files

    # Runs the conversion command for each file in 'in_dir'
    def __run_conversion__(self):
        print("Converting: \n")

        base_command = "python -m spacy convert"
        command_list = []
        list_of_files = self.__check_dir__()

        for file in list_of_files:
            print("\t" + file)
            command = base_command + f" {file} {self.out_dir} --converter {self.CONVERTER} --file-type {self.FILE_TYPE} -n 10"
            command_list.append(command)
            
        print() 

        with ThreadPoolExecutor() as executor:
            results = executor.map(os.system, command_list)

        for result in results:
            if result != 0:
                print(f"Command failed with exit code {result}")

        print("Conversion Successful.\n")
        
    def run(self): 
        self.__run_conversion__()

def main():
    in_dir = r"data/raw"
    out_dir = r"data/processed"
    c2s = Conllu2Spacy(in_dir, out_dir, 'conllu')
    c2s.run()

if __name__ == "__main__":
    main()
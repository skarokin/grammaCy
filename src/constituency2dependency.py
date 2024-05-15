# converts PTB constituency trees to CoNLL-U dependency trees
# uses Stanford CoreNLP conversion script (make sure you have this installed)
# augmentor.py expects CoNLL-U, ensure you run this if your data is PTB format (like OntoNotes 5.0)
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

class Constituency2Dependency:
    FILE_TYPE = "parse"

    def __init__(self, in_dir, out_dir):
        self.in_dir = in_dir
        self.out_dir = out_dir

    def __find_ptb_files__(self):
        files = []
        count = 0
        for root, _, filenames in os.walk(self.in_dir):  
            for file in filenames:
                if file.endswith(self.FILE_TYPE):
                    files.append(os.path.join(root, file))
                    count += 1
        print(f"found {count} .parse files")
        return files
    
    def __convert__(self):       
        print("converting... \n")
        base_command = "java -mx1g edu.stanford.nlp.trees.ud.UniversalDependenciesConverter -treeFile {} > {}"

        exceptions = []
        command_list = []

        for file in self.__find_ptb_files__():
            input_file = file
            output_file = os.path.join(self.out_dir, os.path.basename(file).replace(".parse", ".conllu"))
            command = base_command.format(input_file, output_file)
            command_list.append(command)

        with ThreadPoolExecutor() as executor:
            results = executor.map(subprocess.run, command_list)

        for result in results:
            if result.returncode != 0:
                exceptions.append(result.returncode)
        
        print(f"could not convert {[e for e in exceptions]}")
        print(f"conversion complete! \n")

    def run(self):
        self.__convert__()
    
def main():
    in_dir = r"C:\Users\seank\Downloads\ontonotes-release-5.0\data\files\data\english\annotations"
    out_dir = "data/raw"
    c2d = Constituency2Dependency(in_dir, out_dir)
    c2d.run()

if __name__ == "__main__":
    main()
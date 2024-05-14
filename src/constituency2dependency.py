# converts PTB constituency trees to CoNLL-U dependency trees
# uses Stanford CoreNLP conversion script (make sure you have this installed)
# augmentor.py expects CoNLL-U, ensure you run this if your data is PTB format (like OntoNotes 5.0)
# FUTURE: multithread; this takes like 2.5 hours for OntoNotes 
import os
import subprocess

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
    
    # um for some reason i cant get this check working hahahaha so this is just here for future me to fix
    def __check_corenlp__(self):
        check_command = "java -mx1g edu.stanford.nlp.trees.ud.UniversalDependenciesConverter"

        try:
            result = subprocess.run(check_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stderr.decode()  # The error message is likely to be in stderr, not stdout

            expected_output = "No input file specified!\n\nUsage: java edu.stanford.nlp.trees.ud.UniversalDependenciesConverter [-treeFile trees.tree | -conlluFile deptrees.conllu] [-addFeatures] [-replaceLemmata] [-correctPTB] [-textFile trees.txt] [-outputRepresentation basic|enhanced|enhanced++ (default: basic)]"

            if output == expected_output:
                print("Stanford CoreNLP is installed correctly.")
                return True
            else:
                print("Unexpected output from Stanford CoreNLP, ensure it's installed properly:\n", output)
                return False

        except subprocess.CalledProcessError as e:
            print("Command failed:", e.stderr.decode())
            return False
    
    def __convert__(self):       
        print("converting... \n")
        base_command = "java -mx1g edu.stanford.nlp.trees.ud.UniversalDependenciesConverter -treeFile {} > {}"

        exceptions = []

        for file in self.__find_ptb_files__():
            input_file = file
            output_file = os.path.join(self.out_dir, os.path.basename(file).replace(".parse", ".conllu"))
            command = base_command.format(input_file, output_file)

            try:
                print(f"converting {input_file}\n")
                subprocess.run(command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(e)
                exceptions.append(input_file)
        
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
from preprocess import Preprocess

def main():
    preprocess = Preprocess(in_dir="../data/raw", out_dir="../data/processed", format="conllu")
    preprocess.run()

if __name__ == "__main__":
    main()
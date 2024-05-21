import os
import shutil
from random import sample

class TrainDevSplit:

    def __init__(self, source_dir, dev_size=0.2):
        self.source_dir = source_dir
        self.train_dir = os.path.join(source_dir, 'train')
        self.dev_dir = os.path.join(source_dir, 'dev')
        self.dev_size = dev_size

        # create the target directories if they don't exist
        os.makedirs(self.train_dir, exist_ok=True)
        os.makedirs(self.dev_dir, exist_ok=True)

    def split(self):
        # get a list of all files in the source directory
        files = [f for f in os.listdir(self.source_dir) if os.path.isfile(os.path.join(self.source_dir, f))]

        # randomly select 80% of the files for the training set
        train_files = sample(files, int((1-self.dev_size) * len(files)))

        # the remaining files will be the dev set
        dev_files = [f for f in files if f not in train_files]

        # Move the selected files to the train directory
        for file in train_files:
            shutil.move(os.path.join(self.source_dir, file), self.train_dir)

        # Move the remaining files to the dev directory
        for file in dev_files:
            shutil.move(os.path.join(self.source_dir, file), self.dev_dir)
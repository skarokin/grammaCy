import os
import shutil
from random import sample

# Define the source directory and the target directories
source_dir = 'data/processed'
train_dir = os.path.join(source_dir, 'train')
dev_dir = os.path.join(source_dir, 'dev')

# Create the target directories if they don't exist
os.makedirs(train_dir, exist_ok=True)
os.makedirs(dev_dir, exist_ok=True)

# Get a list of all files in the source directory
files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]

# Randomly select 80% of the files for the training set
train_files = sample(files, int(0.8 * len(files)))

# The remaining files will be the dev set
dev_files = [f for f in files if f not in train_files]

# Move the selected files to the train directory
for file in train_files:
    shutil.move(os.path.join(source_dir, file), train_dir)

# Move the remaining files to the dev directory
for file in dev_files:
    shutil.move(os.path.join(source_dir, file), dev_dir)
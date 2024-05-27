import os
import re

in_path = "data/raw/gum"
out_path = "data/raw/gum_cleaned"

sent_id_pat = re.compile(r"#\s(sent_id)\s.*")
text_pat = re.compile(r".*\t.*\t.*\t.*\t.*\t.*\t.*\t.*\t.*\t.*")

files = os.listdir(in_path)

for file in files:
    count = 0
    with open(os.path.join(in_path, file), "r", encoding='utf-8') as f, open(os.path.join(out_path, file), "a", encoding='utf-8') as out_f:
        lines = f.readlines()
        prev_line = ''
        for line in lines:
            sent_id = sent_id_pat.match(line)
            text = text_pat.match(line)
            if text:
                out_f.write(line)
            elif sent_id:
                if prev_line == '\n':
                    out_f.write('\n')
                out_f.write(line[:12] + str(count) + '\n')
                count += 1
            prev_line = line
        out_f.write('\n')
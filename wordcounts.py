import subprocess
import json
from pathlib import Path
import logging
from notifier import Notifier
import datetime

#Load config file
with open('wordcount_config.json', 'r') as f:
    config = json.load(f)

#Load previous word counts
try:
    with open('wordcounts_history.txt', 'r') as f:
        old_counts = f.read()
    old_lines = old_counts.splitlines()
    last_count = int(old_lines[-1].split()[1])
except FileNotFoundError:
    last_count=0

class Count:
    def __init__(self, filename, count):
        self._filename = filename
        self._count = count
        assert type(self._count) is int

    def __repr__(self):
        return f"{self.filename}: {self.count}"

    def __add__(self, other):
        # assert isinstance(other, Count)
        return Count(None, other.count + self.count)

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __int__(self):
        return self._count

    @property
    def filename(self):
        return self._filename

    @property
    def count(self):
        return self._count

class Folder:
    def __init__(self, name, path, files, counts=[]):
        self._name = name
        self._path = path
        self._files = files
        self._counts = []
        #Checks
        assert type(self._files) is list
    
    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def files(self):
        return self._files

    @property
    def counts(self):
        return self._counts

    @counts.setter
    def counts(self, counts):
        assert type(counts) is list
        for count in counts:
            assert isinstance(count, Count)
        
        self._counts = counts

folders = [Folder(name=f.get('name'), path=f.get('path'), files=f.get('files'))
           for f in config['folders']]      

def extract_counts(folder: Folder):
    p = Path(folder.path)
    file_paths = [list(p.glob(filename)) for filename in folder.files]
    flattened_paths =  [y for x in file_paths 
                        for y in x]
    file_strings = ''.join([f"{file_path.resolve()} " for file_path in flattened_paths])
    out = subprocess.Popen(f"wc -w {file_strings}",
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.STDOUT,
                           shell=True)
    stdout, stderr = out.communicate()
    if stderr:
        logging.info(stderr)
    else:
        splits = stdout.decode('utf-8').split()
        num_lines = int(len(splits)/2)
        counts = [Count(filename=flattened_paths[i].name, count=int(splits[2*i])) 
                  for i in range(num_lines-1)]
        folder.counts = counts
    return folder
     
#Extract Word counts 
folders_with_counts = [extract_counts(folder) for folder in folders]

total_word_count = 0
for folder in  folders_with_counts:
    total_word_count += int(sum(folder.counts))
new_words = total_word_count-last_count

with open('wordcounts_history.txt', 'a') as f:
    f.write(f'{datetime.date.today()}\t{total_word_count}\n')

note = Notifier(config['email'])
note.notification("Wordcounts", f"Today you wrote {new_words} words")
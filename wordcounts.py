import subprocess
import json
from pathlib import Path
import logging
from notifier import Notifier

#Load config file
with open('wordcount_config.json', 'r') as f:
    config = json.load(f)

class Count:
    def __init__(self, filename, count):
        self._filename = filename
        self._count = count

    def __repr__(self):
        return f"{self.filename}: {self.count}"

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
    import pdb; pdb.set_trace()
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
        print(num_lines)
        print(len(flattened_paths))
        counts = [Count(filename=flattened_paths[i].name, count=splits[2*i]) 
                  for i in range(num_lines-1)]
        folder.counts = counts
    return folder
     
#Extract Word counts 
folders_with_counts = [extract_counts(folder) for folder in folders]

#Send email
note = Notifier(config['email'])
note.notification("Wordcounts", "")
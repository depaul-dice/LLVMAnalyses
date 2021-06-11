import os, errno

def silent_remove(file: str)->None:
    try:
        os.remove(file)
    except OSError as e: 
        if e.errno != errno.ENOENT: 
            raise 

import os
from app import app
import random
import string


class Storage():
    def __init__(self):
        self.path_to_disk = app.config['UPLOAD_FOLDER']
    def disk(self,type1):
        if type1 == "local":
            self.path_to_disk = app.config['UPLOAD_FOLDER']
        else:
            self.path_to_disk = type1

        save1 = Ab_file(self.path_to_disk)
        return save1

    def random_path(self, len=10):

        str1 = '123456789'
        str2 = 'qwertyuiopasdfghjklzxcvbnm'
        str3 = str2.upper()
        str4 = str1+str2+str3
        ls = list(str4)
        random.shuffle(ls)
        path = ''.join([random.choice(ls) for x in range(len)])

        return path

class Ab_file():
    def __init__(self,path1):
        self.save_path_to_dick = path1

    def put(self,file):
        file.save(os.path.join(self.save_path_to_dick,file.filename))
        return os.path.join(self.save_path_to_dick,file.filename)

    def get(self, name_file):
        f = read(os.path.join(self.save_path_to_dick,name_file))
        return f

    def delete(self, name_file):
        os.remove(os.path.join(self.save_path_to_dick,name_file))
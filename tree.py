class directory(object):
    def __init__(self, name, parent = None):
        self.name = name    #Documents
        self.parent = parent # reference to the directory object which contains this directory
        self.dir = {}  # dict key = sub-directory name, value = directory object
        self.file = {} # dict key = file name, value = file object
        
class file(object):
    def __init__(self, name, size, start):
        self.name = name   #readme.txt
        self.size = size
        self.used = 0
        self.start = start
            
class fd():
    def __init__(self, file, mode):
        self.file = file # able to access file's attributes: name,size,used,start
        self.pos  = 0
        self.mode = mode
        
class fs(object):
    def __init__(self, name, size):
        self.name = name
        self.root = directory(name)
        self.max_size = size
        self.used_size = 0
        self.wd = self.root # working directory
        self.wd_path = "/"       
        self.open_fds = []       
        self.occupied_bytes = [False] * size
        self.fdata = '\0' * size
        
    def write_native(self):
        with open(self.name, 'w') as file:
            file.write(self.fdata)

    def read_fsdata(self, file):
        start = file.start
        end = file.start + file.size
        
        return self.fdata[start:end]
        
    def write_fsdata(self, index, data):
        end = index + len(data)
        self.fdata = self.fdata[0:index] + data + self.fdata[end:]
            
    def chdir(self, dirname):
        # input: a path with no file at the end
        # sets self.wd (and wd_path) to the specified directory
        # note: if an error is encountered, wd is not changed
        current_dir = self.wd
        new_path = strip(self.wd_path)
        if dirname == '':
            pass
        elif dirname[0] == "/":
            # starting at root'
            current_dir = self.root
            # tokens.pop(0) # TODO: check this
        tokens = strip(dirname)
        for item in tokens:
            try:
                if item == '.':
                    # current directory, do nothing
                    continue
                elif item =='..':
                    # parent directory, go up one
                    current_dir = current_dir.parent
                    new_path.pop(-1) # pop the inner-most directory
                else:
                    # directory specified
                    current_dir = current_dir.dir[item]
                    new_path.append(item)
            except Exception as e:
                # print(str(e))
                raise Exception("Error changing directory: could not navigate to " + item + ".")
        self.wd = current_dir
        self.wd_path = '/' + '/'.join(new_path)
        
    def pwd(self):
        return self.wd_path
            
    def open(self, filename, mode):
        fname = get_string_file(filename)
        path  = get_string_path(filename)
        # change directory (if necessary)
        # get the file
        file = self.go_to_file(filename)
        
        f = fd(file, mode)
        self.open_fds.append(f)
        return f
        
    def close(self, fd):
        self.open_fds.remove(fd)

# The function fs.length(fd) will return the current number of bytes actually used in the file, initially 0. The argument fd is the file descriptor. For example, say the file is created with size 100 bytes, and then 3 bytes are written. These will be in bytes 0-2 of the file, and the length will be 3.
    @staticmethod
    def length(fd):
        return fd.file.used
    
    @staticmethod
    def pos(fd):
        return fd.pos
# The function fs.seek(fd,pos) will set the current read/write position to pos. An exception is raised if (a) the argument is negative or (b) greater than the file size or 
# (c) would make the file bytes non-contiguous.it means don't seek through what is currently unwritten in the file data
    @staticmethod
    def seek(fd, pos):
        file_size = fd.file.size 
        file_used = fd.file.used
        if pos < 0 or file_size <= pos or file_used <= pos : # TODO check if any off-by-one situations
            raise Exception("The value of position is not appropriate")
        else:
            fd.pos = pos

#fs.read(fd,nbytes); returns a string; raises an exception if the read would extend beyond the current length of the file    
    def read(self, fd, nbytes):
        file_content = self.read_fsdata(fd.file)
        file_pos = fd.pos
        file_mode = fd.mode
        if file_mode == 'r':
            if fd.file.used >= file_pos + nbytes: #len(file_content) >= file_pos + nbytes:
                fd.pos = fd.pos + nbytes
                return file_content[file_pos:(file_pos+nbytes)]
            else: 
                raise Exception('nbytes is beyond the current length of the file')
        # mode input except 'r', file can't be read
        else:
            raise Exception("file can not be read")
            
                
# fs.write(fd,writebuf), where writebuf is a string   
    def write(self, fd, writebuf):
        file_mode = fd.mode
        file_content = self.read_fsdata(fd.file)
        file_pos = fd.pos
        file_size = fd.file.size
        if file_mode == 'r':
            raise Exception('file can not be changed')
        elif len(writebuf) + file_pos > file_size:
            raise Exception('file size is not enough')
        else:
            if file_pos + len(writebuf) > fd.file.used:
                fd.file.used = file_pos + len(writebuf)
                
            #fd.data = file_content[:file_pos] + writebuf +file_content[file_pos + len(writebuf):]
            self.write_fsdata(fd.file.start + file_pos, writebuf)
            fd.pos = file_pos + len(writebuf)
            self.write_native()

    # For example filename = '/Document/test/readme.txt'       
    def get_path(self, filename):
        #return absolute path
        if filename == '':
            # avoid error when checking empty string index
            pass
        if filename[0] == '/':
            path = '/'.join(filename.split('/')[0:-1])
            if path == '':
                path = "/"
        if filename[0] != "/":
            ab_path = self.wd_path + '/' + filename
            path = '/'.join(ab_path.split('/')[0:-1])
            if path == '':
                path = "/"
        return path
        
    def go_to_path(self, path):
        # input: a path with no file at the end
        # returns the specified directory
        current_dir = self.wd
        
        if path == '':
            # avoid error when checking empty string index
            pass
        elif path[0] == "/":
            # starting at root
            current_dir = self.root
        
        tokens = strip(path)
        for item in tokens:
            try:
                if item == '.':
                    # current directory, do nothing
                    continue
                elif item =='..':
                    # parent directory, go up one
                    current_dir = current_dir.parent
                  
                else:
                    # go to sub-directory of current
                    current_dir = current_dir.dir[item]
           
                    
            except Exception as e:
                raise Exception("Error getting directory: could not find {}".format(item))
                
        return current_dir
   
    def go_to_file(self, filename):
        # input: a path ending with a filename
        # returns the specified file
        
        # navigate to the directory containing the file
        folder = self.go_to_path(get_string_path(filename))
        fname = get_string_file(filename)
        
        if fname not in folder.file:
            raise Exception('File "{}" does not exist in directory {}'.format(fname, folder.name))
            
        return folder.file[fname]
      
    def isdir(self, dirname):
        try:
            if self.go_to_path(dirname) != None:
                return True
            else:
                return False
        except:
            return False
        
        
    def listdir(self,dirname):
        target_dir = self.go_to_path(dirname)
        List = target_dir.dir.keys() +  target_dir.file.keys()
        return List

    def find_spot(self, n):
        # check self.occupied_bytes for n False entries in a row
        start = None
        count = 0
        for i in range(0, self.max_size):
            if self.occupied_bytes[i] == False:
                # if we don't currently have a 0-streak
                if start == None:
                    # mark this as the beginning
                    start = i
                    
                count += 1
                
                if count == n:
                    # found a string of n open bytes!
                    # set the bytes to occupied before we leave
                    for j in range(start, start + n):
                        self.occupied_bytes[j] = True
                    
                    return start
                
            else:
                # byte is occupied, clear our streak
                start = None
                count = 0
                
        # end of for loop, didn't find room
        return None
        
    def free_spot(self, file):
        # clear occupied bytes to free space for new files
        for i in range(file.start, file.start + file.size):
            self.occupied_bytes[i] = False
    
    def create(self, filename, nbytes):
        file_name = get_string_file(filename)
        target_dir = self.go_to_path(get_string_path(filename))
        if self.max_size < self.used_size + nbytes:
            raise Exception("nbyte is out boundary")
        else:
            # attempt to create the file
            index = self.find_spot(nbytes)
            
            if index != None:
                # we have a spot for our new file
                target_dir.file[file_name] = file(file_name, nbytes, index)
                
                # set bytes to null
                self.fdata = self.fdata[0:index] + '\0' * nbytes + self.fdata[index+nbytes:]
                
                self.used_size += nbytes
            else:
                raise Exception("Error creating file: not enough contiguous room for {} bytes".format(nbytes))

    
    def mkdir(self, dirname):
        #pop the last dir
        # split /Document/test/newdir to /Document/test and newdir
        if dirname[-1] == '/':
            parent_path = get_string_path(dirname[:-1])
        else:
            parent_path = get_string_path(dirname)
        
        new_dir = get_string_lastpath(dirname)
        target_dir = self.go_to_path( parent_path )
        target_dir.dir[new_dir] = directory(name = new_dir, parent = target_dir)

   #reads the entire file, returning a list of strings; treats any 0xa byte it encounters as end of a line; does NOT change the pos value     
    def readlines(self, fd):
        content = self.read_fsdata(fd.file)
        file_mode = fd.mode
        if file_mode == 'r':
            list_str = content[0:fd.file.used].split('\n')
            return list_str
        else:
            raise Exception("file can not be read")
        
    def delfile(self, filename):
        path = get_string_path(filename)
        file_name = get_string_file(filename)
        target_dir = self.go_to_path(path)
        if file_name not in target_dir.file:
            raise Exception("Error deleting file: file does not exist!")
        
        open_files = [x.file for x in self.open_fds]
        if target_dir.file[file_name] in open_files:
            raise Exception("Error deleting file: file is currently open!")
        # free room
        self.free_spot(target_dir.file[file_name])
        target_dir.file.pop(file_name)

# There will be functions fs.delfile(filename) and fs.deldir(dirname) to delete files and directories. Raise an exception if the file/directory doesn't exist or (b) the file is open or (c) the calling process is currently within the specified directory.
    def deldir(self, dirname):
        try:
            target_dir = self.go_to_path(dirname)
        except:
            raise Exception("Error deleting dir: could not find directory!")
            
        dir_name = target_dir.name
        
        import pdb
        # in case user tries to remove root
        if target_dir == self.root:
            raise Exception("Error removing directory: cannot remove root!")
            
        # dealing with situation that direcotory is current working one
        if target_dir == self.wd:
            raise Exception("Error removing directory: target is current working directory!")
            
        open_files = [x.file for x in self.open_fds]
        # check direct parent
        for _, file in target_dir.file.iteritems():
            if file in open_files:
                    raise Exception("Error removing directory: a file in targeted dir is currently open!")
        
        # check any subdirectories of direct parent
        for _, directory in target_dir.dir.iteritems():
            if directory == self.wd:
                raise Exception("Error removing directory: target is in current working directory!")
                
            # check to see if files are open
            for _, file in directory.file.iteritems():
                if file in open_files:
                    raise Exception("Error removing directory: a file in targeted dir is currently open!")
        
        # else, proceed with deleting the directory
        # free space for each file in the directory
        for _, file in target_dir.file.iteritems():
            self.free_spot(file)
        
        # remove directory from parent folder
        target_dir.parent.dir.pop(dir_name)
        

    
# helper func
def strip(path):
    return [x for x in path.split('/') if x != '']
    
def get_string_path(filename):
    # splits the file out of a path and returns the path section as string
    reverse = filename[-1::-1]
    
    # find the first instance of a slash
    try:
        slash = len(filename) - reverse.index('/') - 1
    except:
        slash = 0
        
    return filename[0:slash]
    
def get_string_file(filename):
    # splits the file out of a path and returns the path section as string
    reverse = filename[-1::-1]
    
    # find the first instance of a slash
    try:
        slash = len(filename) - reverse.index('/')
    except:
        slash = None
        
    return filename[slash:]
    
def get_string_lastpath(path):
    if path[-1] == '/':
        # trim last slash so we can get last segment of path
        path = path[:-1]
        
    return get_string_file(path)
# wrapper for tree.py

import tree
import os
import pickle

fileopen = open # make sure we can open our native files

active_fs = None

def no_active_fs(*arg):
    raise Exception("Error: no filesystem has been initialized! Please use fs.init first.")
    
def set_active_fs(fs):
    global active_fs
    global create, mkdir, open, write, delfile, deldir, isdir, chdir, listdir, read, readlines, close
    
    active_fs = fs
    
    # now that an FS has been loaded,
    # point our functions to the fs object
    create    = active_fs.create
    mkdir     = active_fs.mkdir
    open      = active_fs.open
    write     = active_fs.write
    delfile   = active_fs.delfile
    deldir    = active_fs.deldir
    isdir     = active_fs.isdir
    chdir     = active_fs.chdir
    listdir   = active_fs.listdir
    read      = active_fs.read
    readlines = active_fs.readlines
    close     = active_fs.close
    
# all of these functions should not execute until an fs has been initialized
create = mkdir = open = write = delfile = deldir = isdir = chdir = listdir = read = readlines = close = no_active_fs

# these functions don't depend on an fs being loaded
length = tree.fs.length
pos = tree.fs.pos
seek = tree.fs.seek


def init(fsname):
    try:
        size = os.path.getsize(fsname)
        new_fs = tree.fs(fsname, size) # create our filesystem instance
    except Exception as e:
        raise Exception("Error initializing fs: could not get filesize! " + str(e))
        
    set_active_fs(new_fs)
    
def resume(fsname):
    # load fssave
    
    try:
        fssave = fileopen(fsname + '.fssave', 'r')
        fs = pickle.load(fssave)
    except Exception as e:
        raise Exception("Error resuming fs: could not find fssave! " + str(e))
    finally:
        fssave.close()
        
    # load fs data
    try:
        f = fileopen(fsname, 'r')
        fs.fdata = f.read()
    except Exception as e:
        raise Exception("Error resuming fs: could not find fs data! " + str(e))
    finally:
        f.close()

    # fs is all restored and ready to use
    set_active_fs(fs)

def suspend():
    if active_fs == None:
        no_active_fs()
    else:
        # write native file
        try:
            file = fileopen(active_fs.name, 'w')
            
            # save data to file
            file.write(active_fs.fdata)
        except Exception as e:
            print("Error suspending fs: could not write native file.\n" + str(e))
        finally:
            file.close()
        
        try:
            file = fileopen(active_fs.name + '.fssave', 'w')
            
            # clear a few things we don't want to save
            temp_fd = active_fs.open_fds
            temp_dt = active_fs.fdata
            
            active_fs.open_fds = []
            active_fs.fdata = None
            
            # save data to file
            pickle.dump(active_fs, file)
            
            # restore cleared vars
            active_fs.open_fds = temp_fd
            active_fs.fdata = temp_dt
        except Exception as e:
            print("Error suspending fs to file: " + str(e))
        finally:
            file.close()
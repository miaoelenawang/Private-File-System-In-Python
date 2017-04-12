## Private-File-System-In-Python
###This is parallel universe of file system. Instead of using os module, here we develop fs module
<p>An fs system will be created within a native file f specified by the file system administrator</p>
<p>In creating the file system, the user must first call fs.init(fsname).The argument is the name of the native file in which we will do our storage. </p>
<p>The system will have a function <b>fs.create(filename,nbytes)</b>;<b>fs.mkdir(dirname)</b>;<b>fs.open(filename,mode)</b>, where mode is either 'r' or 'w';<b>fs.close(fd)</b>, The argument fd is the file descriptor;<b> fs.length(fd</b>;<b>fs.pos(fd)</b>;<b>fs.seek(fd,pos)</b>;<b>fs.delfile(filename)</b>; <b>fs.deldir(dirname)</b>;<b>fs.isdir(dirname)</b>;<b>fs.chdir(dirname)</b>; <b>fs.listdir(dirname)</b>;and these I/O functions:
<b>fs.read(fd,nbytes)</b>;<b>
fs.write(fd,writebuf)</b>;<b>
fs.readlines(fd)</b></p>
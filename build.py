mac_files = ['main.app']
win_files = ['main.exe','library.zip','python26.dll','w9xpopen.exe']
ignore = ['logfile.txt','lastlog.txt','loghistory.txt','.DS_Store','.hg','.hgignore','.git','.svn','build','build.py']

import os

def copy_file(a,b,type="mac"):
    import shutil
    print "copying file",a
    f = open(a,"rb")
    f2 = open(b,"wb")
    f2.write(f.read())
    f.close()
    f2.close()

def copy_folder(a,b,type="mac"):
    if not os.path.exists(b):
        os.mkdir(b)
    for f in os.listdir(a):
        next = a+"/"+f
        if next.startswith("./"):
            next = next[2:]
        if type=="mac" and next in mac_files and ".app" in next:
            import shutil
            shutil.copytree(next,b+"/"+f)
            continue
        if next in ignore:
	    continue
        if next in mac_files and type!='mac':
            continue
        if next in win_files and type!='win':
            continue
        if os.path.isdir(next):
            copy_folder(next,b+"/"+f,type)
        else:
            copy_file(next,b+"/"+f,type)

def remdir(d):
    for f in os.listdir(d):
        next = d+"/"+f
        if os.path.isdir(next):
            remdir(next)
        else:
            os.remove(next)
    try:
        os.rmdir(d)
    except:
        os.remove(d)

if os.path.exists("build"):
    remdir("build")
if not os.path.exists("build"):
    os.mkdir("build")
copy_folder(".","build/mac","mac")
copy_folder(".","build/win","win")
copy_folder(".","build/src","src")

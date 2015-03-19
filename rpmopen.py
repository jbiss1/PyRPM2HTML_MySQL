#!/usr/bin/python -u
# rpmopen.py: open and extract information from RPM files.
#

import os
import sys
import time
import string
import rpm
import sql
import html
import config

rpm2htmlVerbose = 2
force = 1

#
# Translate the MD5 16 bytes into a 32 char long readable string
#
md5upper="0000000000000000111111111111111122222222222222223333333333333333444444444444444455555555555555556666666666666666777777777777777788888888888888889999999999999999aaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbccccccccccccccccddddddddddddddddeeeeeeeeeeeeeeeeffffffffffffffff"
md5lower="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

def translateMD5(str):
    global md5upper
    global md5lower

    try:
        md5up = string.translate(str, md5upper)
        md5low = string.translate(str, md5lower)
    except:
        return None
    i = 0;
    res = ''
    while i < len(md5up):
        res = res + md5up[i] + md5low[i]
	i = i + 1
    return res

#
# Config crap, to isolate
#

def createDirectory(path):
    if os.access(path, os.W_OK | os.R_OK | os.X_OK) == 0:
	print("createDirectory %s" % (path))
	os.makedirs(path, 0o755)

def checkResourceName(res):
    if res == None or len(res) == 0 or len(res) > 100:
        return 0
    if res[0] == '/':
        isname = 1
    else:
        isname = 0
    # TODO
    return 1
    
def rpmAnalyze(path, nameRpm, h, dir, subdir, stamp, isSource):
    name = h['NAME']
    version = h['VERSION']
    release = h['RELEASE']
    summary = h['SUMMARY']
    description = h['DESCRIPTION']
    distribution = h['DISTRIBUTION']
    if distribution == None:
        distribution = "Unknown"
    info = {}
    info['path'] = path
    info['name'] = name
    info['version'] = version
    info['release'] = release
    info['summary'] = summary
    info['description'] = description
    info['distribution'] = distribution
    info['dir'] = dir
    info['subdir'] = subdir

    if isSource:
        arch = 'src'
    else:
        arch = h['ARCH']
    info['arch'] = arch
    if nameRpm == None:
        nameRpm = "%s-%s-%s.%s.rpm" % (name, version, release, arch)
    os = h['OS']
    info['os'] = os
    try:
	vendor = h['VENDOR']
    except:
        vendor = ''
    if vendor == None:
        vendor = "Unknown"
    info['vendor'] = vendor
    try:
	group = h['GROUP']
    except:
        group = None
    info['group'] = group
    host = h['BUILDHOST']
    info['host'] = host
    size = h['SIZE']
    info['size'] = size

    try:
	tim = h['INSTALLTIME']
    except:
        tim = None
    if tim == None:
	try:
	    tim = h['BUILDTIME']
	except:
	    tim = int(time.time())
    info['time'] = tim
    try:
	srcrpm = h['SOURCERPM']
    except:
        srcrpm = None
    info['srcrpm'] = srcrpm
    try:
	url = h['URL']
    except:
        url = None
    info['url'] = url
    try:
	packager = h['PACKAGER']
    except:
        packager = None
    info['packager'] = packager
    try:
	copyright = h['COPYRIGHT']
    except:
        copyright = None
    info['copyright'] = copyright

    id = sql.sql_add_package(path, name, version, release, arch, 
			      dir['no'], url, srcrpm, vendor, packager, group,
			      summary, description, copyright, tim, size,
			      os, distribution, vendor)
    if id <= 0:
        return

    provides = h['PROVIDES']
    if provides == None:
        if arch != 'src':
	     print("Package %s has no Provides" % (nameRpm))
    else:
	 for provide in provides:
	     sql.sql_add_provide(id, provide)
    info['provides'] = provides
    reqsnames = h['REQUIRENAME']
    reqsflags = h['REQUIREFLAGS']
    reqsvers = h['REQUIREVERSION']
    i = 0
    requires = []
    while i < len(reqsnames):
	try:
	    flag = ''
	    flags = reqsflags[i]
	    if flags & rpm.RPMSENSE_LESS:
	        flag = '<'
	    elif flags & rpm.RPMSENSE_GREATER:
	        flag = '>'
	    if flags & rpm.RPMSENSE_EQUAL:
	        flag = flag + '='
	    if flag != '':
	        requires.append((reqsnames[i], flag, reqsvers[i]))
	    else:
	        requires.append((reqsnames[i], None, None))
	except:
	    print(sys.exc_info()[0], sys.exc_info()[1])
	    pass
	i = i + 1
    info['requires'] = requires
    filenames = h['FILENAMES']
    if filenames == None:
        if arch != 'src':
	     print("Package %s has no Files" % (nameRpm))
    else:
	 for file in filenames:
	     sql.sql_add_file(file, id);
    info['files'] = filenames
    
    md5 = h['SIGMD5']
    if md5 == None:
        print("Package %s has no MD5 checksum" % nameRpm)
    else:
        md5 = translateMD5(md5)
	sql.sql_add_md5(md5, id)
    info['md5'] = md5
       
    changelog = ''
    ctext = h['CHANGELOGTEXT']
    ctime = h['CHANGELOGTIME']
    cname = h['CHANGELOGNAME']
    if ctext == None or ctime == None or cname == None:
        print("Package %s has no Changelog" % path)
    else:
	 i = 0
	 while i < len(ctext):
	     try:
		 t = time.strftime("%a %b %d %Y", time.gmtime(ctime[i]))
		 changelog = changelog + "%s  %s\n" % (t, cname[i])
		 changelog = changelog + "%s\n\n" % (ctext[i])
	     except:
		 pass
	     i = i + 1

    info['changelog'] = changelog
    info['filename'] = nameRpm
    html.dumpRpmHtml(info)
    html.dumpRpmRdf(info)
         
def rpmOpen(nameRpm, dir, subdir):
    print("rpmOpen %s" % (nameRpm))
    if subdir != None:
        buffer = "%s/%s/%s" % (dir['rpmdir'], subdir, nameRpm)
    else:
        buffer = "%s/%s" % (dir['rpmdir'], nameRpm)
    if os.access(buffer, os.R_OK) == 0:
        return

    if force == 0:
	res = sql.sql_get_package_id(buffer)
	if res >= 0:
	    print("package %s is already in the database" % (nameRpm))
	    return

    try:
	fd = os.open(buffer, os.O_RDONLY)

	(h, isSource) = rpm.headerFromPackage(fd)
	os.close(fd)
    except:
        print("Failed to read header of %s" % (buffer))
	return
    cur = rpmAnalyze(buffer, nameRpm, h, dir, subdir, None, isSource)
    return cur
    
def rpmOneDirScan(dir, subdir):
    builtdir = 0
    cur = None

    if dir['rpmdir'] == None:
        print("rpmOneDirScan: dir %s: rpmdir == None" % (dir['name']))
	return

    if subdir != None:
	path = "%s/%s" % (dir['rpmdir'], subdir)
    else:
        path = dir['rpmdir']

    try:
	filenames = os.listdir(path)
    except:
        print("Unable to list directory %s" % (path))
	return
    for filename in filenames:
        if subdir == None:
	    fpath = "%s/%s" % (dir['rpmdir'], filename )
	else:
	    fpath = "%s/%s/%s" % (dir['rpmdir'], subdir, filename )
	if os.access(fpath, os.R_OK) == 0:
	    continue
	if os.path.islink(fpath):
	    print("Skipping symlink %s" % (fpath))
	    continue

	if len(filename) > 4 and  \
	   (filename[-4:] == '.rpm' or filename[-4] == '.spm'):
	    if builtdir == 0:
		if rpm2htmlVerbose > 1:
		    print("Scanning directory %s" % (path))
		if dir['html'] == 1 and config.options['html'] == 1:
		    if subdir != None:
		        tmp = dir['dir']
		    else:
			tmp = "%s/%s" % (dir['dir'], subdir)
		    createDirectory(tmp)
		builtdir = 1
	    cur = rpmOpen(filename, dir, subdir)
	elif len(filename) > 4 and filename[-4:] == '.rdf':
	    # cur = rdfOpen(filename, dir, tree)
	    print("skipping %s" % (filename))
	elif os.path.isdir(fpath):
	    if filename[0] != '.':
		if subdir == None:
		    subtree = filename
		else:
		    subtree = "%s/%s" % (subdir, filename)
		cur = rpmOneDirScan(dir, subtree)
    return cur

def rpmDirScanOneDir(directory):
    print("rpmDirScanOneDir %s" % (directory))
    if directory in config.directories:
        dir = config.directories[directory]
    else:
        print("No information about directory %s" % (directory))
	return

    if ('maint' in dir) == 0 and 'maint' in config.options:
        dir['maint'] = config.options['maint']
    if ('mail' in dir) == 0 and 'mail' in config.options:
        dir['mail'] = config.options['mail']
    if ('ftp' in dir) == 0 and 'ftp' in config.options:
        dir['ftp'] = config.options['ftp']
    if ('ftpsrc' in dir) == 0 and 'ftpsrc' in config.options:
        dir['ftpsrc'] = config.options['ftpsrc']
    if ('dir' in dir) == 0 and 'dir' in config.options:
        dir['dir'] = config.options['dir']
    if ('host' in dir) == 0 and 'host' in config.options:
        dir['host'] = config.options['host']
    if ('name' in dir) == 0 and 'name' in config.options:
        dir['name'] = config.options['name']
    if ('url' in dir) == 0 and 'url' in config.options:
        dir['url'] = config.options['url']

    if ('rpmdir' in dir) == 0:
        print("?!? rpmDir without directory ?!? disabled !")
    elif dir['rpmdir'] == "localbase":
        cur = rpmBaseScan(dir)
    elif ('ftp' in dir) == 0 or dir['ftp'] == None:
        print("Directory %s disabled : no ftp field" % (dir['rpmdir']))
    else:
        dir['no'] = sql.sql_get_distrib_by_directory(dir['rpmdir'])
	if rpm2htmlVerbose:
	    print("Scanning directory %s for RPMs" % (dir['rpmdir']))
	cur = rpmOneDirScan(dir, None)

if __name__ == "__main__":
    sql.readConfigSql()
    print(config.directories)
    rpmDirScanOneDir("/u/veillard/rpms")

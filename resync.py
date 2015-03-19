#!/usr/bin/python -u
import sys
import string
import os
import glob
import sql

#
# we just need the hostname
#
import socket

hostname = socket.gethostname()

#
# We are not interested in parsing errors here
#
import libxml2
def callback(ctx, str):
    return

libxml2.registerErrorHandler(callback, None)

#
# Scan of the filesystem for distributions
#
# comodities
def isnumber(c):
    if ord(c) >= ord('0') and  ord(c) <= ord('9'):
        return 1
    return 0

def exists(f):
    return os.access(f, os.R_OK)

# mapping
def getLocalFTP(path):
    URL = string.replace(path, "/serveur/ftp/",
                               "ftp://%s/" % hostname);
    return URL

def getArchColor(arch):
    if arch == None or arch == "" or arch == "src":
        return

    if arch == "i386" or arch == "i486" or arch == "i586" or arch == "i686" or \
       arch == "athlon" :
        return "#b0ffb0"
    elif arch == "alpha" or arch == "alphaev6":
        return "#ffb0ff"
    elif arch == "sparc" or arch == "sparc64" or arch == "sparcv9":
        return "#b0b0ff"
    elif arch == "noarch":
        return None
    elif arch == "ia64":
        return "#b0b0b0"
    elif arch == "ppc" or arch == "ppc64":
        return "#9aeef6"
    elif arch == "s390" or arch == "s390x":
        return None
    else:
        print("unregistered arch color for %s" % (arch))
    return None

def getArchRemap(arch):
    if arch == "AMD64":
        return "x86_64"
    return arch

# registration
nb_distribs = 0
new_distribs = 0
def registerDist(path, name, html, color,  ftp, ftpsrc, subdir, localmirror):
    global nb_distribs

    nb_distribs = nb_distribs + 1
    if sql.do_sql_query("SELECT ID from Distribs where Directory='%s'" % (path)) < 0:
        return -1
    list = sql.cursor.fetchone()
    if list == None:
        print("Found new dist %s at %s" % (name, path))

    id = int(sql.sql_get_key('Distribs', 'Directory', path))
    if name != None and name != '':
        sql.sql_update_id("Distribs", id, "Name", name)
    if subdir != None and subdir != '':
        sql.sql_update_id("Distribs", id, "Path", subdir)
    if ftp != None and ftp != '':
        sql.sql_update_id("Distribs", id, "URL", ftp)
    if ftpsrc != None and ftpsrc != '':
        sql.sql_update_id("Distribs", id, "URLSrc", ftpsrc)
    if html != None and html != '':
        sql.sql_update_id("Distribs", id, "Html", html)
    if color != None and color != '':
        sql.sql_update_id("Distribs", id, "Color", color)
    if localmirror != None and localmirror != "":
        try:
            sql.cursor.execute("INSERT INTO Mirrors (ID,URL) VALUES (%s,'%s')" % (id, localmirror))
        except:
            pass
        

# Red Hat tree scanner
def getRedHatFTP(path):
    if path == None:
        return None
    URL = string.replace(path, "/serveur/ftp/linux/redhat",
                               "ftp://ftp.redhat.com/pub/redhat/linux");
    return URL
    
def scanRedHatLinuxSources(topdir, version, special=None):
     srpms = glob.glob(topdir + "/*.src.rpm")
     if srpms == [] or srpms == ():
         print("No sources at %s" % (topdir))
	 return
     registerDist(topdir,
                  "Red Hat %s %s Sources" % (special, version),
		  "true",
		  None,
		  getRedHatFTP(topdir),
		  None,
		  "redhat/%s/src" % version,
		  getLocalFTP(topdir));

def scanRedHatLinuxArch(topdir, version, arch, SRPMS, special=None,
                        surname=None):
     topdir = topdir + "/RedHat/RPMS"
     rpms = glob.glob(topdir + "/*." + getArchRemap(arch) + ".rpm")
     if rpms == [] or rpms == ():
         print("No %s rpms at %s" % (arch, topdir))
	 return
     registerDist(topdir,
                  "Red Hat %s %s for %s" % (special, version, arch),
		  "true",
		  getArchColor(getArchRemap(arch)),
		  getRedHatFTP(topdir),
		  getRedHatFTP(SRPMS),
		  "redhat/%s/%s" % (version,arch),
		  getLocalFTP(topdir));

def scanRedHatLinuxOS(OS, version, special="Linux"):
    SRPMS = None
    if (exists(OS + '/i386' + "/SRPMS")):
        scanRedHatLinuxSources(OS + '/i386' + "/SRPMS", version, special)
	SRPMS = OS + '/i386' + "/SRPMS"
    else:
	srpms = glob.glob(OS + '/*' + "/SRPMS")
	if srpms != [] and srpms != ():
	    scanRedHatLinuxSources(srpms[0], version, special)
	    SRPMS = srpms[0]

    arches = ()
    try:
	arches = os.listdir(OS)
    except:
        print("Red Hat dir %s cannot be read" % (OS))
    for arch in arches:
         scanRedHatLinuxArch(OS + "/" + arch, version, arch, SRPMS,
	                     special)

def scanRedHatLinux(topdir, version, special="Linux"):
    if exists(topdir + "/en/as"):
        if special == "Linux":
	    s = "Server"
	else:
	    s = special + " Server"
	scanRedHatLinuxOS(topdir + "/en/as", version, s)
    if exists(topdir + "/en/ws"):
        if special == "Linux":
	    s = "Workstation"
	else:
	    s = special + " Workstation"
	scanRedHatLinuxOS(topdir + "/en/ws", version, s)
    if exists(topdir + "/en/os"):
	scanRedHatLinuxOS(topdir + "/en/os", version, special)

def scanRedHatLinuxUpdatesSources(topdir, version, special="Linux"):
     srpms = glob.glob(topdir + "/*.src.rpm")
     if srpms == [] or srpms == ():
         print("No sources at %s" % (topdir))
	 return
     registerDist(topdir,
                  "Red Hat %s %s Updates Sources" % (special, version),
		  "true",
		  None,
		  getRedHatFTP(topdir),
		  None,
		  "redhat/updates/%s/src" % version,
		  getLocalFTP(topdir));

def scanRedHatLinuxUpdatesArch(topdir, version, arch, SRPMS, special="Linux"):
     rpms = glob.glob(topdir + "/*." + getArchRemap(arch) + ".rpm")
     if rpms == [] or rpms == ():
         if exists(topdir + "/RPMS") and exists(topdir + "/SRPMS"):
	     scanRedHatLinuxUpdatesArch(topdir + "/RPMS", version, arch,
	                                topdir + "/SRPMS")
	 else:
	     # print "No %s rpms at %s" % (arch, topdir)
	     pass
	 return
     registerDist(topdir,
                  "Red Hat %s %s Updates for %s" % (special, version, arch),
		  "true",
		  getArchColor(getArchRemap(arch)),
		  getRedHatFTP(topdir),
		  getRedHatFTP(SRPMS),
		  "redhat/updates/%s/%s" % (version,arch),
		  getLocalFTP(topdir));

def scanRedHatLinuxOSUpdates(OS, version, special="Linux"):
    SRPMS = None
    if (exists(OS + "/SRPMS")):
        scanRedHatLinuxUpdatesSources(OS + "/SRPMS", version, special)
	SRPMS = OS + "/SRPMS"
    arches = ()
    try:
	arches = os.listdir(OS)
    except:
        print("Red Hat dir %s cannot be read" % (OS))
    for arch in arches:
	if arch == "SRPMS":
	    continue
	if arch == "scripts":
	    continue
	if arch == "images":
	    continue
	if arch[0:6] == "kernel":
	    continue
	if arch == "iSeries" or arch == "pSeries":
	    continue
	dir = OS + "/" + arch
        scanRedHatLinuxUpdatesArch(OS + "/" + arch, version, arch, SRPMS, special)

def scanRedHatLinuxUpdates(topdir, version, special="Linux"):
    if exists(topdir + "/en/as"):
        if special == "Linux":
	    s = "Server"
	else:
	    s = special + " Server"
        scanRedHatLinuxOSUpdates(topdir + "/en/as", version, special);
    if exists(topdir + "/en/aw"):
        if special == "Linux":
	    s = "Workstation"
	else:
	    s = special + " Workstation"
        scanRedHatLinuxOSUpdates(topdir + "/en/aw", version, special);
    if exists(topdir + "/en/os"):
        scanRedHatLinuxOSUpdates(topdir + "/en/os", version, special);
    
def scanRedHatEnterpriseUpdates(topdir):
    try:
	files = os.listdir(topdir)
    except:
        print("Red Hat dir %s cannot be read" % (topdir))
    dists = []
    for file in files:
        scanRedHatLinuxUpdates(topdir + "/" + file, file, "Enterprise")
        

def scanRedHatUpdates(topdir):
    try:
	files = os.listdir(topdir)
    except:
        print("Red Hat dir %s cannot be read" % (topdir))
    dists = []
    for file in files:
	if file[0] == '.':
	    continue
	elif file[0:3] == "ls-":
	    continue
        elif file == "beta":
	    continue
	elif file == "enterprise":
	    scanRedHatEnterpriseUpdates(topdir + "/" + file)
	elif isnumber(file[0]):
	    scanRedHatLinuxUpdates(topdir + "/" + file, file)
	elif file == "other_prod":
	    continue
	elif file == "current":
	    continue
	elif file == "images":
	    continue
	else:
	    print("unhandled %s" % (file))

def scanRedHatBeta(topdir):
    try:
	betas = os.listdir(topdir)
    except:
        print("Red Hat dir %s cannot be read" % (topdir))
    for beta in betas:
        scanRedHatLinux(topdir + "/" + beta, beta, "Beta")

def scanRedHatPreview(topdir):
    try:
	previews = os.listdir(topdir)
    except:
        print("Red Hat dir %s cannot be read" % (topdir))
    for preview in previews:
        scanRedHatLinux(topdir + "/" + preview, preview, "Preview")

def scanRedHatEnterprise(topdir):
    try:
	enterps = os.listdir(topdir)
    except:
        print("Red Hat dir %s cannot be read" % (topdir))
    for enterp in enterps:
        scanRedHatLinux(topdir + "/" + enterp, enterp, "Enterprise")

def scanRedHat(topdir):
    try:
	files = os.listdir(topdir)
    except:
        print("Red Hat dir %s cannot be read" % (topdir))
    dists = []
    for file in files:
	if file[0] == '.':
	    continue
	elif file[0:3] == "ls-":
	    continue
        elif file == "beta":
	    scanRedHatBeta(topdir + "/" + file)
	elif file == "updates":
	    scanRedHatUpdates(topdir + "/" + file)
	elif file == "updates":
	    scanRedHatUpdates(topdir + "/" + file)
	elif file == "preview":
	    scanRedHatPreview(topdir + "/" + file)
	elif file == "enterprise":
	    scanRedHatEnterprise(topdir + "/" + file)
	elif isnumber(file[0]):
	    scanRedHatLinux(topdir + "/" + file, file)
	elif file == "code":
	    continue
	elif file == "current":
	    continue
	else:
	    print("unhandled %s" % (file))

# SuSE scanner
def getSuSEFTP(path):
    if path == None:
        return None
    URL = string.replace(path, "/serveur/ftp/linux/SuSE-Linux",
                               "ftp://ftp.suse.com:/pub/suse");
    return URL
    
def scanSuSELinuxArchDistUpdates(topdir, version, arch):
    SRPMS=None
    if exists(topdir + "/rpm/src"):
        SRPMS = topdir + "/rpm/src"
    registerDist(topdir,
	      "SuSE Linux %s Updates for %s" % (version, arch),
	      "true",
	      getArchColor(arch),
	      getSuSEFTP(topdir),
	      getSuSEFTP(SRPMS),
	      "suse/updates/%s/%s" % (version,arch),
	      getLocalFTP(topdir));

def scanSuSELinuxArchUpdates(topdir, arch):
    try:
	dists = os.listdir(topdir)
    except:
        print("SuSE dir %s cannot be read" % (topdir))
	return
    for file in dists:
        if file[0] == '.':
	    continue
	elif file[0:3] == "ls-":
	    continue
	elif file[0:6] == "README":
	    continue
	elif file == "current":
	    continue
	elif file == "products":
	    continue
	elif file == "supplementary":
	    continue
	elif isnumber(file[0]):
	    scanSuSELinuxArchDistUpdates(topdir + "/" + file, file, arch)

def scanSuSELinuxArchDist(topdir, version, arch):
    SRPMS=None
    if exists(topdir + "/suse/src"):
        SRPMS = topdir + "/suse/src"
    if exists(topdir + "/suse"):
        registerDist(topdir,
                  "SuSE Linux %s for %s" % (version, arch),
		  "true",
		  getArchColor(arch),
		  getSuSEFTP(topdir),
		  getSuSEFTP(SRPMS),
		  "suse/%s/%s" % (version,arch),
		  getLocalFTP(topdir));

def scanSuSELinuxArch(topdir, arch):
    try:
	dists = os.listdir(topdir)
    except:
        print("SuSE dir %s cannot be read" % (topdir))
	return
    for file in dists:
        if file[0] == '.':
	    continue
	elif file[0:3] == "ls-":
	    continue
	elif file[0:6] == "README":
	    continue
	elif file == "current":
	    continue
	elif file == "products":
	    continue
	elif file == "update":
	    scanSuSELinuxArchUpdates(topdir + "/" + file, arch)
	elif file == "supplementary":
	    continue
	elif isnumber(file[0]):
	    scanSuSELinuxArchDist(topdir + "/" + file, file, arch)
    
def scanSuSE(topdir):
    try:
	files = os.listdir(topdir)
    except:
        print("SuSE dir %s cannot be read" % (topdir))
    for file in files:
	if file[0] == '.':
	    continue
	elif file[0:3] == "ls-":
	    continue
	elif file[0:6] == "README":
	    continue
	elif file[0:7] == "pubring":
	    continue
	elif file == "noarch":
	    continue
	elif file == "SuSEFax_WIN32":
	    continue
	elif file == "current":
	    continue
	else:
	    scanSuSELinuxArch(topdir + "/" + file, file)

def getFreshrpmsFTP(path):
    if path == None:
        return None
    URL = string.replace(path, "/serveur/ftp/linux/freshrpms",
                               "ftp://freshrpms.net/pub/freshrpms");
    return URL
    
def scanFreshrpmsLinuxDefine(topdir, version, name, rel):
    registerDist(topdir,
	      "Freshrpms Updates for %s" % (version),
	      "true",
	      None,
	      getFreshrpmsFTP(topdir),
	      None,
	      "freshrpms/%s/%s" % (name,rel),
	      getLocalFTP(topdir));

def scanFreshrpmsLinuxDist(topdir, dist, name):
    try:
	files = os.listdir(topdir)
    except:
        print("Freshrpms dir %s cannot be read" % (topdir))
    for file in files:
        if file[0] == '.':
	    continue
	elif file[0:3] == "ls-":
	    continue
	elif file[0:6] == "README":
	    continue
	elif file == "current":
	    continue
	elif file == "misc":
	    scanFreshrpmsLinuxDefine(topdir + "/" + file, dist + " Misc",
	                             name, file)
	elif file == "testing":
	    scanFreshrpmsLinuxDefine(topdir + "/" + file, dist + " Testing",
	                             name, file)
	elif file == "rawhide":
	    scanFreshrpmsLinuxDefine(topdir + "/" + file, dist + " Rawhide",
	                             name, file)
	else:
	    scanFreshrpmsLinuxDefine(topdir + "/" + file, dist + " " + file,
	                             name, file)
    
def scanFreshrpms(topdir):
    try:
	files = os.listdir(topdir)
    except:
        print("Freshrpms dir %s cannot be read" % (topdir))
    for file in files:
	if file[0] == '.':
	    continue
	elif file[0:3] == "ls-":
	    continue
	elif file[0:6] == "README":
	    continue
	elif file == "RPM-GPG-KEY":
	    continue
	elif file == "ayo":
	    continue
	elif file == "redhat":
	    scanFreshrpmsLinuxDist(topdir + "/" + file, "Red Hat", file)
	elif file == "yellowdog":
	    scanFreshrpmsLinuxDist(topdir + "/" + file, "Yellowdog", file)
	else:
	    print("unhandled Freshrpms %s" % (file))
def scanDist():
    sql.sql_delete_distrib("/serveur/ftp/linux/SuSE-Linux")
    sql.sql_delete_distrib("/serveur/ftp/linux/freshrpms")
    scanRedHat("/serveur/ftp/linux/redhat")
    scanSuSE("/serveur/ftp/linux/SuSE-Linux")
    scanFreshrpms("/serveur/ftp/linux/freshrpms")
    print("Found %d distributions" % (nb_distribs))

#
# Synchronization of mirrors info
#
def sync_mirror(name, URL):
    query = string.replace(URL, 'search.php', 'servers.php')
    try:
        doc = libxml2.parseFile(query)
    except:
        print("failed to lookup servers from %s" % (name))
	return
    ctxt = doc.xpathNewContext()
    try:
        count = ctxt.xpathEval("string(/servers/@count)");
        servers = ctxt.xpathEval("//server")
    except:
        print("failed to find servers from %s servers list" % (name))
	return
    print("%s exports %s servers" % (name, count))
    for server in servers:
        try:
	    Rname = server.xpathEval("string(name)");
	    RURL = server.xpathEval("string(URL)");
	    query = "INSERT INTO Searches (URL, name, active) VALUES \
	                   ('%s', '%s', 1)" % (RURL, Rname)
	    try:
		sql.cursor.execute(query)
            except:
	         # ignore overwrites
	         pass
	except:
	    print("failed to read record from %s servers list" % (name))
    doc.freeDoc()
    query = string.replace(URL, 'search.php', 'distribs.php')
    try:
        doc = libxml2.parseFile(query)
    except:
        print("failed to lookup distribs from %s" % (name))
	return
    ctxt = doc.xpathNewContext()
    try:
        count = ctxt.xpathEval("string(/distribs/@count)");
        distribs = ctxt.xpathEval("//distrib")
    except:
        print("failed to find distribs from %s distribs list" % (name))
	return
    print("%s exports %s distribs" % (name, count))
    for distrib in distribs:
        try:
	    Directory = distrib.xpathEval("string(Directory)");
	    if exists(Directory):
	        table = 'Distribs'
            else:
	        table = 'OldDistribs'
	    id = int(sql.sql_get_key(table, 'Directory', Directory))
	    Name = distrib.xpathEval("string(Name)");
	    if Name != None and Name != '':
		sql.sql_update_id(table, id, "Name", Name)
	    Vendor = distrib.xpathEval("string(Vendor)");
	    if Vendor != None and Vendor != '':
		sql.sql_update_id(table, id, "Vendor", Vendor)
	    Path = distrib.xpathEval("string(Path)");
	    if Path != None and Path != '':
		sql.sql_update_id(table, id, "Path", Path)
	    RURL = distrib.xpathEval("string(URL)");
	    if RURL != None and RURL != '':
		sql.sql_update_id(table, id, "URL", RURL)
	    URLSrc = distrib.xpathEval("string(URLSrc)");
	    if URLSrc != None and URLSrc != '':
		sql.sql_update_id(table, id, "URLSrc", URLSrc)
	    Html = distrib.xpathEval("string(Html)");
	    if Html != None and Html != '':
		sql.sql_update_id(table, id, "Html", Html)
	    Color = distrib.xpathEval("string(Color)");
	    if Color != None and Color != '':
		sql.sql_update_id(table, id, "Color", Color)
	    Description = distrib.xpathEval("string(Description)");
	    if Description != None and Description != '':
		sql.sql_update_id(table, id, "Description",
				   Description)
	except:
	    print("failed to read record from %s servers list" % (name))
    doc.freeDoc()
    query = string.replace(URL, 'search.php', 'mirrors.php')
    try:
        doc = libxml2.parseFile(query)
    except:
        print("failed to lookup mirrors from %s" % (name))
	return
    ctxt = doc.xpathNewContext()
    try:
        count = ctxt.xpathEval("string(/mirrors/@count)");
        dists = ctxt.xpathEval("//dist")
    except:
        print("failed to find mirrors from %s mirrors list" % (name))
	return
    print("%s exports %s mirrors" % (name, count))
    for dist in dists:
        try:
	    rname = dist.xpathEval("string(@name)");
	    id = int(sql.sql_read_key('Distribs', rname))
	    mirrors = dist.xpathEval(".//mirror");
	    for mirror in mirrors:
	        try:
		    RURL=mirror.xpathEval("string(.)");
		    country=mirror.xpathEval("string(@country)");
		    if country != None and country != "":
			sql.cursor.execute("INSERT INTO Mirrors (ID,URL,Country) \
			                 VALUES (%s,'%s', '%s')" %
					(id, RURL, country))
		    else:
			sql.cursor.execute("INSERT INTO Mirrors (ID,URL) \
			                 VALUES (%s,'%s')" %
					(id, RURL))
		except:
		    pass
	except:
	    print("failed to read record from %s mirrors list" % (name))
    doc.freeDoc()
    #
    # Avoid reintroducing deleted distro after mirroring
    #
    sql.sql_delete_distrib("/serveur/ftp/linux/SuSE-Linux")
    sql.sql_delete_distrib("/serveur/ftp/linux/freshrpms")

def sync_mirrors():
    if sql.do_sql_query("SELECT name, URL from Searches") < 0:
        return -1
    list = sql.cursor.fetchone()
    lists = []
    # store in lists because sync_mirror destroys the sql.cursor.
    while list != None:
        name = list[0]
	if name == 'fr2':
	    list = sql.cursor.fetchone()
	    continue
	URL = list[1]
	if hostname == 'rpmfind.net':
	    if name != 'rpmfind':
	        lists.append((name, URL))
	elif hostname == 'speakeasy.rpmfind.net':
	    if name != 'speakeasy':
	        lists.append((name, URL))
	elif hostname == 'fr.rpmfind.net':
	    if name != 'fr':
	        lists.append((name, URL))
	list = sql.cursor.fetchone()
    for list in lists:
        name = list[0]
	URL = list[1]
	sync_mirror(name, URL);

def dump_local_config():
    conf = open("rpm2html-local.config", "w")
    conf.write(""";
; Configuration file for rpm2html-1.0
;  See http://www.nongnu.org/rpm2html/
;
; Generated from the database by resync.py
;
; maintainer of the local rpm mirror
maint=Daniel Veillard
; mail for the maintainer
mail=daniel@veillard.com
; Directory to store the HTML pages produced
dir=/serveur/ftp/linux/RPM
; The relative URL for front pages
url=/linux/RPM
; Export the local packages in HTML format
html=true
; Export the local packages in RDF format
rdf=false
rdf_dir=
; Protect e-mails from SPAM bots by mangling them in HTML output
protectemails=true
; Compile a list of resources in RDF format
rdf_resources=false
rdf_resources_dir=
; Extra headers in generated pages
header=http://rpmfind.net/linux/rpm2html/mirrors.html Mirrors
header=http://rpmfind.net/linux/rpm2html/help.html Help
header=http://rpmfind.net/linux/rpm2html/search.php Search
; Build the tree for the distributions
tree=true
;
; Configuration for an RPM directory
;
; [The name between brackets is the directory, NEEDED !]
; name=A significant name for this mirror, NEEDED !
; ftp=The original FTP/HTTP url, NEEDED !
; ftpsrc=Where the associated sources are stored
; subdir=subdirectory for generated pages
; color=Background color for pages
; url= relative URL for pages in this directory
; URL can be defined for mirrors the first one is the 'local' one
;
""")
    if sql.do_sql_query("SELECT ID,Name, Directory, Path, URL, URLSrc, Html, Color from Distribs") < 0:
        return -1
    distribs = {}
    list = sql.cursor.fetchone()
    while list != None:
        try:
	    (ID,Name,Directory,Path,URL,URLSrc,Html,Color) = list
	    os.stat(Directory)
	    ID=int(ID)
	except:
	    list = sql.cursor.fetchone()
	    continue
	if Name != None and Name != "" and Path != None and Path != "" and \
	    URL != None and URL != "":
	    distribs[ID] = [list, ()];
	list = sql.cursor.fetchone()

    for ID in list(distribs.keys()):
        if sql.do_sql_query("SELECT URL from Mirrors where ID=%s" % ID) < 0:
	    continue
	mirrors = sql.cursor.fetchall()
	distribs[ID][1] = mirrors
	
    for ID in list(distribs.keys()):
        list = distribs[ID][0];
	(id,Name,Directory,Path,URL,URLSrc,Html,Color) = list
        mirrors = distribs[ID][1];

	conf.write("[%s]\n"% Directory)
	conf.write("name=%s\n"% Name)
	if Html != None and Html != "":
	    conf.write("html=%s\n"% Html)
	conf.write("ftp=%s\n"% URL);
	if URLSrc != None and URLSrc != "":
	    conf.write("ftpsrc=%s\n"% URLSrc)
	conf.write("subdir=%s\n"% Path);
	if Color != None and Color != "":
	    conf.write("color=%s\n"% Color)
	for mirror in mirrors:
	    conf.write("mirror=%s\n"% mirror)
	conf.write("\n")
    
    conf.close()
    print("Dumped %d distrib info to rpm2html-local.config\n" % (
          len(list(distribs.keys()))))
    
if __name__ == "__main__":
    sql.sql_check_tables()
    print("#\n# Scanning repository for distribs\n#")
    scanDist()
    print("#\n# Syncing with other mirrors\n#")
    sync_mirrors()
    print("#\n# Checking Distribs\n#")
    sql.sql_check_distribs()
    print("#\n# Generating a new config file\n#")
    dump_local_config()
#    sql.sql_check_packages()
    print("#\n# Cleanup SQL tables\n#")
    sql.sql_cleanup_tables()
    print("#\n# Stats on server %s\n"% (hostname))
    sql.sql_show_stats()

#    sql.sql_get_top_queries(20)

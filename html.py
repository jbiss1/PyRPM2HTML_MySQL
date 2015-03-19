#!/usr/bin/python
#
# serialization of package information as HTML
# 
import string
import rpmopen
import time
import os
import config

rpm2html_rpm2html_name = 'rpm2html'
rpm2html_rpm2html_ver = '1.0'
rpm2html_rpm2html_url = "http://www.nongnu.org/rpm2html/"
rpm2html_help = "http://rpmfind.net/linux/rpm2html/help.html"
rpm2html_search = "/linux/rpm2html/search.php"

localizedStrings = {
    "LANG_FROM": "from",
    "LANG_NAME": "Name",
    "LANG_DISTRIBUTION": "Distribution",
    "LANG_VERSION": "Version",
    "LANG_VENDOR": "Vendor",
    "LANG_RELEASE": "Release",
    "LANG_BUILD_DATE": "Build date",
    "LANG_GROUP": "Group",
    "LANG_BUILD_HOST": "Build host",
    "LANG_SIZE": "Size",
    "LANG_RPM_SRC": "Source",
    "LANG_SUMMARY": "Summary",
    "LANG_PACKAGER": "Packager",
    "LANG_URL": "URL",
    "LANG_INDEX": "Index",
    "LANG_INDEX_HTML": "index.html",
    "LANG_GROUP_HTML": "Groups.html",
    "LANG_VENDOR_HTML": "Vendors.html",
    "LANG_BYDATE_HTML": "ByDate.html",
    "LANG_BYNAME_HTML": "ByName.html",
    "LANG_DISTRIB_HTML": "Distribs.html",
    "LANG_SORTED_BY_GROUP": "index by Group",
    "LANG_SORTED_BY_DISTRIB": "index by Distribution",
    "LANG_SORTED_BY_VENDOR": "index by Vendor",
    "LANG_SORTED_BY_CDATE": "index by creation date",
    "LANG_SORTED_BY_NAME": "index by Name",
    "LANG_PROVIDES": "Provides",
    "LANG_REQUIRES": "Requires",
    "LANG_COPYRIGHT": "Copyright",
    "LANG_SIGNATURES": "Signatures",
    "LANG_CHANGELOG": "Changelog",
    "LANG_FILES": "Files",
}

html_flags = {
    "" : "",
    "<": "&lt;",
    "<=": "&lt;=",
    ">": "&gt;",
    ">=": "&gt;=",
    "=": "=",
}

def extractEMail(str):
    return None

def convertHTML(str):
    res = ''
    for c in str:
        n = ord(c)
	if c == '\n' or c == '\r' or c == '\t' or c == ' ': res = res + c
        elif n ==  34: res = res + "&quot;"
        elif n ==  38: res = res + "&amp;"
        elif n ==  60: res = res + "&lt;"
        elif n ==  62: res = res + "&gt;"
        elif n == 160: res = res + "&nbsp;"
        elif n == 161: res = res + "&iexcl;"
        elif n == 162: res = res + "&cent;"
        elif n == 163: res = res + "&pound;"
        elif n == 164: res = res + "&curren;"
        elif n == 165: res = res + "&yen;"
        elif n == 166: res = res + "&brvbar;"
        elif n == 167: res = res + "&sect;"
        elif n == 168: res = res + "&uml;"
        elif n == 169: res = res + "&copy;"
        elif n == 170: res = res + "&ordf;"
        elif n == 171: res = res + "&laquo;"
        elif n == 172: res = res + "&not;"
        elif n == 173: res = res + "&shy;"
        elif n == 174: res = res + "&reg;"
        elif n == 175: res = res + "&macr;"
        elif n == 176: res = res + "&deg;"
        elif n == 177: res = res + "&plusmn;"
        elif n == 178: res = res + "&sup;"
        elif n == 179: res = res + "&sup;"
        elif n == 180: res = res + "&acute;"
        elif n == 181: res = res + "&micro;"
        elif n == 182: res = res + "&para;"
        elif n == 183: res = res + "&middot;"
        elif n == 184: res = res + "&cedil;"
        elif n == 185: res = res + "&sup;"
        elif n == 186: res = res + "&ordm;"
        elif n == 187: res = res + "&raquo;"
        elif n == 188: res = res + "&frac;"
        elif n == 189: res = res + "&frac;"
        elif n == 190: res = res + "&frac;"
        elif n == 191: res = res + "&iquest;"
        elif n == 192: res = res + "&Agrave;"
        elif n == 193: res = res + "&Aacute;"
        elif n == 194: res = res + "&Acirc;"
        elif n == 195: res = res + "&Atilde;"
        elif n == 196: res = res + "&Auml;"
        elif n == 197: res = res + "&Aring;"
        elif n == 198: res = res + "&AElig;"
        elif n == 199: res = res + "&Ccedil;"
        elif n == 200: res = res + "&Egrave;"
        elif n == 201: res = res + "&Eacute;"
        elif n == 202: res = res + "&Ecirc;"
        elif n == 203: res = res + "&Euml;"
        elif n == 204: res = res + "&Igrave;"
        elif n == 205: res = res + "&Iacute;"
        elif n == 206: res = res + "&Icirc;"
        elif n == 207: res = res + "&Iuml;"
        elif n == 208: res = res + "&ETH;"
        elif n == 209: res = res + "&Ntilde;"
        elif n == 210: res = res + "&Ograve;"
        elif n == 211: res = res + "&Oacute;"
        elif n == 212: res = res + "&Ocirc;"
        elif n == 213: res = res + "&Otilde;"
        elif n == 214: res = res + "&Ouml;"
        elif n == 215: res = res + "&times;"
        elif n == 216: res = res + "&Oslash;"
        elif n == 217: res = res + "&Ugrave;"
        elif n == 218: res = res + "&Uacute;"
        elif n == 219: res = res + "&Ucirc;"
        elif n == 220: res = res + "&Uuml;"
        elif n == 221: res = res + "&Yacute;"
        elif n == 222: res = res + "&THORN;"
        elif n == 223: res = res + "&szlig;"
        elif n == 224: res = res + "&agrave;"
        elif n == 225: res = res + "&aacute;"
        elif n == 226: res = res + "&acirc;"
        elif n == 227: res = res + "&atilde;"
        elif n == 228: res = res + "&auml;"
        elif n == 229: res = res + "&aring;"
        elif n == 230: res = res + "&aelig;"
        elif n == 231: res = res + "&ccedil;"
        elif n == 232: res = res + "&egrave;"
        elif n == 233: res = res + "&eacute;"
        elif n == 234: res = res + "&ecirc;"
        elif n == 235: res = res + "&euml;"
        elif n == 236: res = res + "&igrave;"
        elif n == 237: res = res + "&iacute;"
        elif n == 238: res = res + "&icirc;"
        elif n == 239: res = res + "&iuml;"
        elif n == 240: res = res + "&eth;"
        elif n == 241: res = res + "&ntilde;"
        elif n == 242: res = res + "&ograve;"
        elif n == 243: res = res + "&oacute;"
        elif n == 244: res = res + "&ocirc;"
        elif n == 245: res = res + "&otilde;"
        elif n == 246: res = res + "&ouml;"
        elif n == 247: res = res + "&divide;"
        elif n == 248: res = res + "&oslash;"
        elif n == 249: res = res + "&ugrave;"
        elif n == 250: res = res + "&uacute;"
        elif n == 251: res = res + "&ucirc;"
        elif n == 252: res = res + "&uuml;"
        elif n == 253: res = res + "&yacute;"
        elif n == 254: res = res + "&thorn;"
        elif n == 255: res = res + "&yuml;"
	elif n > 32: res = res + c
    return res

def convertXML(str):
    res = ''
    for c in str:
        n = ord(c)
	if c == '\n' or c == '\r' or c == '\t' or c == ' ': res = res + c
        elif n ==  34: res = res + "&quot;"
        elif n ==  38: res = res + "&amp;"
        elif n ==  60: res = res + "&lt;"
        elif n ==  62: res = res + "&gt;"
	elif n > 32 and n < 0x80 : res = res + c
    return res

def dumpDirIcon():
    # TODO
    pass

def checkDate(filename,stamp):
    try:
        return os.stat(filename)[8] > stamp
    except:
        return 0

def checkDirectory(filename):
    try:
        return os.path.isdir(filename)
    except:
        return 0
    
def checkFile(filename):
    try:
        return os.access(filename, os.R_OK)
    except:
        return 0

def rpmSoftwareName(rpm):
    return "%s-%s-%s" % (rpm['name'], rpm['version'], rpm['release'])

def rpmName(rpm):
    if rpm['arch'] != None:
	return "%s-%s-%s.%s" % (rpm['name'], rpm['version'], rpm['release'],
	                        rpm['arch'])
    else:
	return "%s-%s-%s" % (rpm['name'], rpm['version'], rpm['release'])

def cleanName(str):
    res = ''
    for c in str:
	if c == '/' or c == ' ' or c == '"' or c == '\'' or \
	   c == '<' or c == '>' or c == ':' or c == '|' or \
	   c == '@' or c == '\t' or c == '\n' or c == '\r' :
	    res = res + '_'
	else:
	    res = res + c
    return res

def escapeName(str):
    res = ''
    for tmp in str:
        if (((tmp >= 'a') and (tmp <= 'z')) or
            ((tmp >= 'A') and (tmp <= 'Z')) or
	    ((tmp >= '0') and (tmp <= '9')) or
	    (tmp == '-') or (tmp == '_') or (tmp == '.') or
	    (tmp == '!') or (tmp == '~') or (tmp == '*') or (tmp == '\'') or
	    (tmp == '(') or (tmp == ')')):
	    res = res + tmp
	else:
	    res = res + '%' + hex(ord(tmp))
    return res

def groupName(str):
    return cleanName(str) + ".html"
def distribName(str):
    return cleanName(str) + ".html"
def vendorName(str):
    return cleanName(str) + ".html"
def resourceName(str):
    return cleanName(str) + ".html"

def fullURL(dir, subdir, filename):
    if dir == None:
        return "http://%s%s" % (rpm2html_host, config.options['url'])
    if subdir == None:
        return "http://%s%s/%s" % (rpm2html_host, config.options['url'], filename)
    return "http://%s%s/%s/%s" % (rpm2html_host, config.options['url'], subdir, filename)

def fullPathName(dir, subdir, filename):
    if dir == None:
        return "%s/%s" % (rpm2html_dir, filename)
    if subdir == None:
        return "%s/%s" % (dir['dir'], filename)
    return "%s/%s/%s" % (dir['dir'], subdir, filename)

def fullPathNameLr(dir, subdir, filename, letter):
    if dir == None:
        return "%s/%s%s" % (rpm2html_dir, letter, filename)
    if subdir == None:
        return "%s/%s%s" % (dir['dir'], letter, filename)
    return "%s/%s/%s%s" % (dir['dir'], subdir, letter, filename)

def fullPathNameNr(dir, subdir, filename, number):
    if dir == None:
        return "%s/%s%s" % (rpm2html_dir, number, filename)
    if subdir == None:
        return "%s/%s%s" % (dir['dir'], number, filename)
    return "%s/%s/%s%s" % (dir['dir'], subdir, number, filename)


def generateHtmlHeader(html, title, color):
    html.write("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\">\n")
    html.write("<html>\n<head>\n<title>%s</title>\n" % (title))
    html.write("<meta name=\"GENERATOR\" content=\"%s %s\">\n" %
            (rpm2html_rpm2html_name, rpm2html_rpm2html_ver))
    if color == None:
        html.write("</head>\n<body bgcolor=\"#ffffff\" text=\"#000000\">\n")
    else :
        html.write("</head>\n<body bgcolor=\"%s\" text=\"#000000\">\n" %
	        (color))

def generateHtmlFooter(html):
    html.write("<hr>\n")
    html.write("<p>%s <a href=\"%s\">%s %s</a>\n" % (
            "Generated by",
	    rpm2html_rpm2html_url, rpm2html_rpm2html_name,
	    rpm2html_rpm2html_ver))
    if rpm2html_help != None:
	html.write("<p><a href=\"%s\">%s</a>, %s\n" % (
		rpm2html_help, config.options['maint'], time.asctime(time.gmtime(time.time()))))
    else:
	html.write("<p><a href=\"mailto:%s\">%s</a>, %s\n" % (
		config.options['mail'], config.options['maint'], time.asctime(time.gmtime(time.time()))))
    html.write("</body>\n</html>\n")

def generateHtmlRpmAnchor(html, cur):
    if cur['dir'] == None:
	html.write("<a href=\"\">")
	return
    
    dir = cur['dir']
    if dir['subdir'] != None:
	if cur['subdir'] != None:
	    if dir['url'] != None:
		html.write("<a href=\"%s/%s/%s/%s.html\">" % (
			dir['url'], dir['subdir'],
			cur['subdir'], rpmName(cur)))
	    else:
		html.write("<a href=\"%s/%s/%s.html\">" % (
			cur['subdir'], dir['subdir'], rpmName(cur)))
	else:
	    if dir['url'] != None:
		html.write("<a href=\"%s/%s/%s.html\">" % (
		        dir['url'], dir['subdir'], rpmName(cur)))
	    else:
		html.write("<a href=\"%s/%s.html\">" % (
		        dir['subdir'], rpmName(cur)))
	
    else:
        if ((cur['subdir'] != None) and (cur['subdir'][0] != '\0')) :
	    if dir['url'] != None:
		html.write("<a href=\"%s/%s/%s.html\">" % (
			dir['url'], cur['subdir'], rpmName(cur)))
	    else:
		html.write("<a href=\"%s/%s.html\">" % (
			cur['subdir'], rpmName(cur)))
	else :
	    if dir['url'] != None:
		html.write("<a href=\"%s/%s.html\">" % (
		        dir['url'], rpmName(cur)))
	    else:
		html.write("<a href=\"%s.html\">" % ( rpmName(cur)))
	
def generateLinks(html):
    html.write("<table border=5 cellspacing=5 cellpadding=5>\n")
    html.write("<tbody>\n<tr>\n")

    html.write("<td><a href=\"%s/%s\">%s</a></td>\n" % (
            config.options['url'], localizedStrings['LANG_INDEX_HTML'],
	    localizedStrings['LANG_INDEX']))
    html.write("<td><a href=\"%s/%s\">%s</a></td>\n" % (
            config.options['url'], localizedStrings['LANG_GROUP_HTML'],
	    localizedStrings['LANG_SORTED_BY_GROUP']))
    html.write("<td><a href=\"%s/%s\">%s</a></td>\n" % (
            config.options['url'], localizedStrings['LANG_DISTRIB_HTML'],
	    localizedStrings['LANG_SORTED_BY_DISTRIB']))
    html.write("<td><a href=\"%s/%s\">%s</a></td>\n" % (
            config.options['url'], localizedStrings['LANG_VENDOR_HTML'],
	    localizedStrings['LANG_SORTED_BY_VENDOR']))
    html.write("<td><a href=\"%s/%s\">%s</a></td>\n" % (
	    config.options['url'], localizedStrings['LANG_BYDATE_HTML'],
	    localizedStrings['LANG_SORTED_BY_CDATE']))
    html.write("<td><a href=\"%s/%s\">%s</a></td>\n" % (
            config.options['url'], localizedStrings['LANG_BYNAME_HTML'],
	    localizedStrings['LANG_SORTED_BY_NAME']))

    for header in config.extra_headers:
        name = header[0]
        url = header[1]
	if url[0] == '/' or url[0:7] == "http://" or url[0:6] == "ftp://" or \
	   url[0:7] == "mailto:":
	    html.write("<td><a href=\"%s\">%s</a></td>\n" % (url, name))
	else:
	    html.write("<td><a href=\"%s/%s\">%s</a></td>\n" % (
	            config.options['url'], url, name))
    html.write("</tr>\n</tbody></table>\n")

def dumpRpmHtml(rpm):
    if config.options['html'] == 0:
        return

    dir = rpm['dir']

    if dir['subdir'] != None:
        if rpm['subdir'] != None:
	    buf = "%s/%s/%s" % (dir['dir'], dir['subdir'], rpm['subdir'])
	else:
	    buf = "%s/%s" % (dir['dir'], dir['subdir'])
    else:
        if rpm['subdir'] != None:
	    buf = "%s/%s" % (dir['dir'], rpm['subdir'])
	else:
	    buf = "%s" % (dir['dir'])
    rpmopen.createDirectory(buf)
    buf = buf + "/" + rpmName(rpm) + ".html"

    try:
	html = open(buf, "w")
	print("Writing %s" % buf)
    except:
        print("Couldn't save to file %s" % (buf))
        return

    buf = "%s RPM" % (rpmName(rpm))
    generateHtmlHeader(html, buf, None)
    generateLinks(html)

    if rpm['subdir'] != None:
	html.write("<h1 align=center><a href=\"%s/%s/%s\">\n" % (
	    dir['ftp'], rpm['subdir'], rpm['filename']))
    else:
	html.write("<h1 align=center><a href=\"%s/%s\">\n" % (
	    dir['ftp'], rpm['filename']))
    
    if rpm['arch']:
        if rpm['arch'] == "src":
	    html.write("%s-%s-%s Source RPM</a></h1>\n" % (
	            rpm['name'], rpm['version'], rpm['release']))
        else:
	    html.write("%s-%s-%s RPM for %s</a></h1>\n" % (
		rpm['name'], rpm['version'], rpm['release'], rpm['arch']))
    else:
	html.write("%s-%s-%s RPM</a></h1>\n" % (
            rpm['name'], rpm['version'], rpm['release']))
    

    if dir['ftp']:
        html.write("<h3 align=center>%s <a href=\"%s\">%s</a></h3>\n" % (
	      localizedStrings['LANG_FROM'],
	      dir['ftp'], dir['name']))
    

    html.write("<table align=center border=5 cellspacing=5 cellpadding=5 bgcolor=\"%s\">" % ( dir['color']))
    html.write("<tbody>\n")
    html.write("<tr><td>%s: %s</td>\n" % (
	    localizedStrings['LANG_NAME'],
            rpm['name']))
    html.write("<td>%s: <a href=\"%s/%s\">%s</a></td></tr>\n" % (
	    localizedStrings['LANG_DISTRIBUTION'], config.options['url'],
            distribName(rpm['distribution']),
	    convertHTML(rpm['distribution'])))
    html.write("<tr><td>%s: %s</td>\n" % (
	    localizedStrings['LANG_VERSION'],
            rpm['version']))
    html.write("<td>%s: <a href=\"%s/%s\">%s</a></td></tr>\n" % (
	    localizedStrings['LANG_VENDOR'], config.options['url'],
            vendorName(rpm['vendor']), convertHTML(rpm['vendor'])))
    buf = time.strftime("%c", time.localtime((rpm['time'])))
    html.write("<tr><td>%s: %s</td>\n<td>%s: %s</td></tr>\n" % (
	    localizedStrings['LANG_RELEASE'],
	    rpm['release'],
	    localizedStrings['LANG_BUILD_DATE'],
	    buf))
    
    if config.options['url'] != None:
	html.write("<tr><td>%s: <a href=\"%s/%s\">%s</a></td>\n" % (
		localizedStrings['LANG_GROUP'], config.options['url'],
		groupName(rpm['group']), convertHTML(rpm['group'])))
    else:
	html.write("<tr><td>%s: <a href=\"%s\">%s</a></td>\n" % (
		localizedStrings['LANG_GROUP'],
		groupName(rpm['group']), convertHTML(rpm['group'])))
    html.write("<td>%s: %s</td></tr>\n" % (
	    localizedStrings['LANG_BUILD_HOST'], rpm['host']))
    html.write("<tr><td>%s: %d</td>\n" % (
	    localizedStrings['LANG_SIZE'],
            rpm['size']))
    if dir['ftpsrc']:
	html.write("<td>%s: <a href=\"%s/%s\">%s</a></td></tr>\n" % (
	        localizedStrings['LANG_RPM_SRC'],
		dir['ftpsrc'], rpm['srcrpm'], rpm['srcrpm']))
    else:
	html.write("<td>%s: %s</td></tr>\n" % (
	        localizedStrings['LANG_RPM_SRC'],
		rpm['srcrpm']))
    
    if rpm['packager']:
        email = extractEMail(rpm['packager'])
	if email == None:
	    html.write("<tr><td colspan=\"2\">%s: %s</td></tr>\n" % (
		    localizedStrings['LANG_PACKAGER'],
		    convertHTML(rpm['packager'])))
        else:
	    html.write("<tr><td colspan=\"2\">%s: <a href=\"mailto:%s\">%s</a></td></tr>\n" % (
		    localizedStrings['LANG_PACKAGER'],
		    email, convertHTML(rpm['packager'])))
    
    if rpm['url'] != None:
	html.write("<tr><td colspan=\"2\">%s: <a href=\"%s\">%s</a></td></tr>\n" % (
		localizedStrings['LANG_URL'],
		rpm['url'], rpm['url']))
    html.write("<tr><td colspan=\"2\">%s: %s</td></tr>\n" % (
	    localizedStrings['LANG_SUMMARY'],
            convertHTML(rpm['summary'])))
    html.write("</tbody>\n</table>\n")
    html.write("<pre>%s\n</pre>\n" % ( convertHTML(rpm['description'])))
    if rpm['provides'] != None:
        provides = rpm['provides']
	if len(provides) > 0:
	    html.write("<h3>%s</h3>\n" % (localizedStrings['LANG_PROVIDES']))
	    html.write("<ul>\n")
	    for provide in provides:
		if rpm2html_search != None:
		    html.write("<li><a href=\"%s?query=%s\">%s</a>\n" % (
			rpm2html_search, escapeName(provide), provide))
		elif config.options['url'] != None:
		    html.write("<li><a href=\"%s/%s\">%s</a>\n" % (
			config.options['url'], resourceName(provide), provide))
		else:
		    html.write("<li><a href=\"%s\">%s</a>\n" % (
			   resourceName(provide), provide))
	    html.write("</ul>\n")
	
    if rpm['requires'] != None:
        requires = rpm['requires']
	if len(requires) > 0:
	    html.write("<h3>%s</h3>\n" % (localizedStrings['LANG_REQUIRES']))
	    html.write("<ul>\n")
	    for reqs in requires:
	        (require, cmp, version) = reqs
		if len(require) >= 8 and require[0:7] == 'rpmlib(':
		    continue
		if string.find(require, '(GLIBC') >= 0:
		    continue
		if rpm2html_search != None:
		    html.write("<li><a href=\"%s?query=%s\">%s</a>" % (
			rpm2html_search, escapeName(require), require))
		elif config.options['url'] != None:
		    html.write("<li><a href=\"%s/%s\">%s</a>" % (
			config.options['url'], resourceName(require), require))
		else:
		    html.write("<li><a href=\"%s\">%s</a>" % (
			   resourceName(require), require))
		if cmp != None and version != None:
		    html.write(" %s %s\n" % (html_flags[cmp], version))
		else:
		    html.write("\n")
	    html.write("</ul>\n")


    if rpm['copyright']:
        html.write("<h3>%s</h3>\n" %
	    localizedStrings['LANG_COPYRIGHT'])
	html.write("<pre>%s\n</pre>\n" % (convertHTML(rpm['copyright'])))

    if rpm['md5']:
        html.write("<h3>%s</h3>\n" % (localizedStrings['LANG_SIGNATURES']))
	html.write("<pre>internal MD5: %s</pre>\n" % (rpm['md5']))

    if rpm['changelog']:
        html.write("<h3>%s</h3>\n" % (localizedStrings['LANG_CHANGELOG']))
	html.write("<pre>%s\n</pre>\n" % convertHTML(rpm['changelog']))
    
    html.write("<h3>%s</h3>\n" % (localizedStrings['LANG_FILES']))
    if rpm['files'] == None:
	html.write("<bold>%s</bold>\n" % localizedStrings['LANG_NO_FILES'])
    else:
	html.write("<pre>");
	for file in rpm['files']:
	    html.write("%s\n" % (file))
	html.write("</pre>\n");
    
    generateHtmlFooter(html)
    html.close()

def dumpRpmRdf(rpm):
    if 'rdf' not in config.options or \
        config.options['rdf_resources'] == 0:
	return -1
    if 'rdf_dir' not in config.options or \
        config.options['rdf_dir'] == None:
	return -1

    rdf_dir = config.options['rdf_dir']
    dir = rpm['dir']

    filename = rpm['path']
    rpmdir = dir['rpmdir']
    if rpmdir[-1] == '/':
	rpmdir = rpmdir[0:-1]
    l = len(rpmdir)
    if filename[0:l] == rpmdir:
	filename = filename[l:]
	subdir=dir['subdir']
	index = string.rfind(filename, '/')
	if index > 0:
	    psubdir = filename[0:index]
	    if psubdir[0] == '/':
		psubdir=psubdir[1:]
	else:
	    psubdir = ''
	ftp = dir['ftp']
	if filename[0] != '/' and ftp[-1] != '/':
	    filename = '/' + filename
    else:
        print("Package %s outside of dist subdir %s" % (filename, rpmdir))
	return -1

    if dir['subdir'] != None:
        if rpm['subdir'] != None:
	    buf = "%s/%s/%s" % (rdf_dir, dir['subdir'], rpm['subdir'])
	else:
	    buf = "%s/%s" % (rdf_dir, dir['subdir'])
    else:
        if rpm['subdir'] != None:
	    buf = "%s/%s" % (rdf_dir, rpm['subdir'])
	else:
	    buf = "%s" % (rdf_dir)
    rpmopen.createDirectory(buf)
    buf = buf + "/" + rpmName(rpm) + ".rdf"

    try:
	rdf = open(buf, "w")
	print("Writing %s" % buf)
    except:
        print("Couldn't save to file %s" % (buf))
        return -1

    deep = string.count(rpm['subdir'], '/') + string.count(dir['subdir'], '/')
    dotdot = "../" * deep

    rdf.write("<?xml version=\"1.0\"?>\n")
    rdf.write("<rdf:RDF xmlns:RDF=\"http://www.w3.org/TR/WD-rdf-syntax#\" xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\" xmlns:RPM=\"http://www.rpm.org/\">\n")

    rdf.write("  <rdf:Description about=\"%s%s\">\n" % (ftp, filename))
    rdf.write("    <RPM:Name>%s</RPM:Name>\n" % (rpm['name']))
    rdf.write("    <RPM:Version>%s</RPM:Version>\n" % (rpm['version']))
    rdf.write("    <RPM:Release>%s</RPM:Release>\n" % (rpm['release']))
    if 'url' in rpm and rpm['url'] != None:
	rdf.write("    <RPM:URL>%s</RPM:URL>\n" % (rpm['url']))
    rdf.write("    <RPM:Arch>%s</RPM:Arch>\n" % (rpm['arch']))
    rdf.write("    <RPM:Os>%s</RPM:Os>\n" % (rpm['os']))
    if 'distribution' in rpm and rpm['distribution'] != None:
	rdf.write("    <RPM:Distribution>%s</RPM:Distribution>\n" % (
	          convertXML(rpm['distribution'])))
    else:
	rdf.write("    <RPM:Distribution>Unknown</RPM:Distribution>\n")
    if 'packager' in rpm and rpm['packager'] != None:
	rdf.write("    <RPM:Vendor>%s</RPM:Vendor>\n" % (
	          convertXML(rpm['packager'])))
    else:
	rdf.write("    <RPM:Vendor>Unknown</RPM:Vendor>\n")
    if 'group' in rpm and rpm['group'] != None:
	rdf.write("    <RPM:Group>%s</RPM:Group>\n" % (
	          convertXML(string.strip(rpm['group']))))
    else:
	rdf.write("    <RPM:Group>Unknown</RPM:Group>\n")
    if 'summary' in rpm and rpm['summary'] != None:
	rdf.write("    <RPM:Summary>%s</RPM:Summary>\n" % (
	          convertXML(string.strip(rpm['summary']))))
    else:
	rdf.write("    <RPM:Summary></RPM:Summary>\n")
    if 'description' in rpm and rpm['description'] != None:
	rdf.write("    <RPM:Description>%s</RPM:Description>\n" % (
	          convertXML(string.strip(rpm['description']))))
    else:
	rdf.write("    <RPM:Description></RPM:Description>\n")
    if 'copyright' in rpm and rpm['copyright'] != None:
	rdf.write("    <RPM:Copyright>%s</RPM:Copyright>\n" % (
	          convertXML(string.strip(rpm['copyright']))))
    else:
	rdf.write("    <RPM:Copyright>Unknown</RPM:Copyright>\n")
    if 'changelog' in rpm and rpm['changelog'] != None:
	rdf.write("    <RPM:Changelog>%s</RPM:Changelog>\n" % (
	          convertXML(string.strip(rpm['changelog']))))
    else:
	rdf.write("    <RPM:Changelog>Unknown</RPM:Changelog>\n")
    if 'srcrpm' in rpm and rpm['srcrpm'] != None:
	rdf.write("    <RPM:Sources>%s</RPM:Sources>\n" % (
	          rpm['srcrpm']))
    buf = time.strftime("%c", time.localtime((rpm['time'])))
    rdf.write("    <RPM:BuildDate>%s</RPM:BuildDate>\n" % (buf))
    rdf.write("    <RPM:Date>%s</RPM:Date>\n" % (rpm['time']))
    rdf.write("    <RPM:Size>%s</RPM:Size>\n" % (rpm['size']))
    if 'host' in rpm and rpm['host'] != None:
	rdf.write("    <RPM:BuildHost>%s</RPM:BuildHost>\n" % (
	          convertXML(rpm['host'])))

    if 'files' in rpm and rpm['files'] != None:
	rdf.write("    <RPM:Files>")
	for file in rpm['files']:
	    rdf.write("%s\n" % (convertXML(file)))
	rdf.write("</RPM:Files>\n")
    rdf.write("  </rdf:Description>\n")
    rdf.write("</rdf:RDF>\n")
    rdf.close()

if __name__ == "__main__":
    print(convertHTML("""ceci est un petit test
des capacites du convertisseur HTML
a + b < c
Trond Eivind Glomsrřd <teg@redhat.com>
"""));

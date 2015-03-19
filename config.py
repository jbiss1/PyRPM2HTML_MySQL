#!/usr/bin/python3 -u
#
# module to parse the configuration file
#
import sys
import string
import sql

rpm2htmlVerbose = 10

options = {}
extra_headers = []
metadata_mirrors = []
metadata = {}
directories = {}


def rpmDirSearch(dirname):
    global directories

    if dirname in directories:
        return directories[dirname]
    dir = {}
    dir['color'] = "#ffffff"
    if 'dir' in options:
        dir['dir'] = options['dir']
    else:
        dir['dir'] = None
    dir['files'] = 0
    dir['html'] = 1
    dir['subdir'] = None
#    dir['htmlpath'] = ''
#    dir['rpmpath'] = ''
    dir['ftp'] = None
    dir['ftpsrc'] = None
    dir['host'] = None
    dir['mail'] = None
    dir['maint'] = None
    dir['name'] = None
    dir['nb_mirrors'] = 0
    dir['mirrors'] = []
    dir['rpmdir'] = dirname
    dir['size'] = 0
    dir['trust'] = None
    dir['url'] = None
    dir['build_tree'] = 0
    dir['follow_symlinks'] = 0
    dir['rpm_symlinks'] = 0
    directories[dirname] = dir
    return dir
    
def addConfigEntry(rpmdir, name, value):
    global options
    global extra_headers
    global metadata_mirrors
    global rpm2htmlVerbose

    if rpm2htmlVerbose > 1:
        print("addConfigEntry(\"%s\", \"%s\", \"%s\")\n" % (rpmdir, name, value))

    if rpmdir == 'rpm2html':
        if name == 'url' or name == 'maint' or name == 'help' or name == 'mail' or name == 'dir' or name == 'ftp' or name == 'ftpsrc' or name == 'name' or name == 'host' or name == 'subdir' or name == 'rdf_dir' or name == 'rdf_resources_dir':
            options[name] = value
        elif name == 'tree' or name == 'rdf' or name == 'rdf_resources' or name == 'html':
            if value == 'true' or value == 'yes':
                options[name] = 1
            elif value == 'false' or value == 'no':
                options[name] = 0
            else:
                print("Global option %s ignored use values yes or no" % (name))
        elif name == 'header':
            extra_headers.append((name, value))
        else:
            print("Global option unknown: %s" % (name))
            options[name] = value


    elif rpmdir == 'metadata':
        if name == 'mirror':
            metadata_mirrors.append(value)

    else:
        cur = rpmDirSearch(rpmdir)
        if name == 'url' or name == 'name' or name == 'subdir' or name == 'dbpath' or name == 'dir' or name == 'ftp' or name == 'ftpsrc' or name == 'color' or name == 'trust' or name == 'host' or name == 'rdf_dir':
            cur[name] = value
        elif name == 'tree' or name == 'followsymlinks' or name == 'rpmsymlinks' or name == 'html':
            if value == 'true' or value == 'yes':
                cur[name] = 1
            elif value == 'false' or value == 'no':
                cur[name] = 0
            else:
                print("Global option %s ignored use values yes or no" % (name))
        elif name == 'mirror' or name == 'mirrors':
            cur['mirrors'].append(value)
        else:
            print("Option unknown: %s for [%s] unknown" % (name, rpmdir))
            cur[name] = value

def readConfigFile(filename):
    try:
        config = open(filename, 'r')
    except:
        print("Unable to read %s" % (filename))
        return -1

    rpmdir = 'rpm2html'
    for line in config.readlines():
        if line[0] == '#':
            continue
        if line[0] == ';':
            continue
        line = line.strip()
        if len(line) == 0:
            continue
        if line[0] == '[':
            fields = line.rstrip(']')
            if len(fields) > 0:
                rpmdir = fields[0]
                continue
        fields = line.split('=')
        if len(fields) > 1:
            name = fields[0].strip()
            value = fields[1].strip()
            addConfigEntry(rpmdir, name, value)
            sql.sqlConfigEntry(rpmdir, name, value)
        elif len(fields) > 0:
            print("Config %s: unable to parse line %s" % (line))
    config.close()
        
        
if __name__ == "__main__":
    global directories
    global options

    readConfigFile("rpm2html-local.config")
    print("Read %d global options and %d directory descriptions" % (
          len(list(options.keys())), len(list(directories.keys()))))
    sql.close_sql()
         

#!/usr/bin/python3 -u
import sys
import os
#import sqlite3
import pymysql
pymysql.install_as_MySQLdb() #makes pymysql function as MySQLdb
#
# General database access
#
db = None
cursor = None
rpm2htmlVerbose = 10

def init_sql():
    global db
    global cursor

    try:
        myhost = os.environ["MySQL_HOST"]
    except:
        myhost = '192.168.1.4'

    try:
        mybase = os.environ["MySQL_BASE"]
    except:
        mybase = 'python_rpm2html'

    try:
        user = os.environ["MySQL_USER"]
    except:
        user = 'python'

    try:
        passwd = os.environ["MySQL_PASS"]
    except:
        passwd = 'python'

    try:
        db = pymysql.connect(host=myhost, user=user, passwd=passwd, db=mybase)
        cursor = db.cursor()
    except:
        print("failed to connect to MySQL(%s@%s)" % (user, myhost))
        print(sys.exc_info()[0], sys.exc_info()[1])
        sys.exit(1)
        db = None
        cursor = None

def close_sql():
    global cursor

    if cursor != None:
        cursor.close()
    cursor = None
    db = None
        
#
# Generic functions to access the tables
#
def do_sql_query(query, mycursor = None):
    global cursor

    if mycursor == None:
        mycursor = cursor
    if cursor == None:
        init_sql()
        mycursor = cursor
    
    try:
        mycursor.execute(query)
    except:
        print("do_sql_query: %s failed" % (query))
        print(sys.exc_info()[0], sys.exc_info()[1])
        return -1
    return 0


def sql_update_id(table, id, field, value):
    global cursor

    if cursor == None:
        init_sql()
    try:
        cursor.execute("UPDATE %s SET %s='%s' WHERE ID=%s" %
               (table, field, value, id))
    except:
        print("sql_update_id: %s:%s failed" % (table, id))
        print(sys.exc_info()[0], sys.exc_info()[1])
        return -1
    return 0

def sql_blind_insert(table, key, value, id):
    global cursor

    if cursor == None:
        init_sql()
    if id > 0:
        try:
            cursor.execute("INSERT INTO %s (ID, %s) VALUES (%s, '%s')" %
               (table, id, key, value))
        except:
            print("sql_blind_insert: %s:%s failed" % (table, id))
            print(sys.exc_info()[0], sys.exc_info()[1])
            return -1
    else:
        try:
            cursor.execute("INSERT INTO %s (%s) VALUES ('%s')" %
                   (table, key, value))
        except:
            print("sql_blind_insert: %s:%s failed" % (table, id))
            print(sys.exc_info()[0], sys.exc_info()[1])
            return -1
    return cursor.lastrowid
    
def sql_update(table, name, field, value):
    global cursor

    if cursor == None:
        init_sql()
    try:
        cursor.execute("SELECT ID FROM %s WHERE Name='%s'" % (table, name))
        result = cursor.fetchone()
    except:
        print("sql_update: %s:%s failed to find id" % (table, name))
        print(sys.exc_info()[0], sys.exc_info()[1])
        return -1
    if result == None:
        try:
            cursor.execute("INSERT INTO %s (Name,%s) VALUES ('%s','%s')" %
               (table, field, name, value))
        except:
            print("sql_update: %s:%s failed to insert" % (table, name))
            print(sys.exc_info()[0], sys.exc_info()[1])
            return -1
    else:
        print(result[0])
        id = result[0]
        try:
            cursor.execute("UPDATE %s SET %s='%s' WHERE ID=%d" %
               (table, field, value, id))
        except:
            print("sql_update: %s:%s failed to update" % (table, name))
            print(sys.exc_info()[0], sys.exc_info()[1])
            return -1
    
def sql_get_key(table, name, value):
    global cursor

    if cursor == None:
        init_sql()
    try:
        cursor.execute("SELECT ID FROM %s WHERE %s='%s'" %
               (table, name, value))
        result = cursor.fetchone()
    except:
        print("sql_get_key: %s:%s failed to find id" % (table, name))
        print(sys.exc_info()[0], sys.exc_info()[1])
        return -1
    if result == None:
        return int(sql_blind_insert(table, name, value, -1))
    return int(result[0])
    
def sql_read_key(table, name):
    global cursor

    if cursor == None:
        init_sql()
    try:
        cursor.execute("SELECT ID FROM %s WHERE Name='%s'" %
               (table, value))
        result = cursor.fetchone()
    except:
        return -1
    if result == None:
        return -1
    return int(result[0])
    
def sql_read_info_key(table, name, value):
    global cursor

    if cursor == None:
        init_sql()
    try:
        cursor.execute("SELECT ID FROM %s WHERE %s='%s'" %
               (table, name, value))
        result = cursor.fetchone()
    except:
        print("sql_update: %s:%s failed to find id" % (table, name))
        print(sys.exc_info()[0], sys.exc_info()[1])
        return -1
    if result == None:
        return -1
    return int(result[0])
    
#
# Tables handling
#
def sql_rebuild_table(table):
    if table == "Config":
        query = """CREATE TABLE Config (
            ID int(11) NOT NULL auto_increment,
            Name varchar(50) NOT NULL,
            Value varchar(255),
            PRIMARY KEY (ID),
            KEY Name (Name(10))
    )"""
    elif table == "Vendors":
        query = """CREATE TABLE Vendors (
            ID int(11) NOT NULL auto_increment,
            Name varchar(255) NOT NULL,
            URL varchar(255),
            Key1 text,
            Key2 text,
            Key3 text,
            Description text,
            PRIMARY KEY (ID),
            KEY Name (Name(10))
    )"""
    elif table == "Distributions":
        query = """CREATE TABLE Distributions (
            ID int(11) NOT NULL auto_increment,
            Name varchar(255) NOT NULL,
            URL varchar(255),
            Key1 text,
            Key2 text,
            Key3 text,
            Description text,
            PRIMARY KEY (ID),
            KEY Name (Name(10))
    )"""
    elif table == "Searches":
        query = """CREATE TABLE Searches (
            URL varchar(255) NOT NULL,
            name varchar(255) NOT NULL,
            active int,
            UNIQUE(URL),
            UNIQUE(name)
    )"""
    elif table == "Mirrors":
        query = """CREATE TABLE Mirrors (
            ID int(11),
            URL varchar(255) NOT NULL,
            Country int(11),
            UNIQUE(URL)
    )"""
    elif table == "Metadata":
        query = """CREATE TABLE Metadata (
            URL varchar(255) NOT NULL,
            Maintainer int(11),
            Country int(11),
            UNIQUE(URL)
    )"""
    elif table == "Distribs":
        query = """CREATE TABLE Distribs (
            ID int(11) NOT NULL auto_increment,
            Name varchar(255) NOT NULL,
            Vendor int(11),
            Directory varchar(255),
            Path varchar(100) NOT NULL,
            URL varchar(255),
            URLSrc varchar(255),
            Html varchar(8),
            Color varchar(10),
            Key1 text,
            Key2 text,
            Description text,
            PRIMARY KEY (ID),
            KEY Name (Name(10))
    )"""
    elif table == "OldDistribs":
        query = """CREATE TABLE OldDistribs (
            ID int(11) NOT NULL auto_increment,
            Name varchar(255) NOT NULL,
            Vendor int(11),
            Directory varchar(255),
            Path varchar(100) NOT NULL,
            URL varchar(255),
            URLSrc varchar(255),
            Html varchar(8),
            Color varchar(10),
            Key1 text,
            Key2 text,
            Description text,
            PRIMARY KEY (ID),
            KEY Name (Name(10))
    )"""
    elif table == "Packages":
        query = """CREATE TABLE Packages (
            ID int(11) NOT NULL auto_increment,
            filename varchar(255) NOT NULL,
            Name varchar(50) NOT NULL,
            Version varchar(50) NOT NULL,
            Release varchar(50) NOT NULL,
            Arch varchar(15) NOT NULL,
            Dist int(11),
            URL varchar(255),
            URLSrc varchar(255),
            Vendor int(11),
            Packager int(11),
            Category varchar(255),
            Summary varchar(255),
            Description text,
            Copyright varchar(255),
            Date int(11),
            Size int(11),
            Os varchar(12),
            PRIMARY KEY (ID),
            KEY filename (filename(80)),
            KEY Name (Name(15))
    )"""
    elif table == "Files":
        query = """CREATE TABLE Files (
            ID int(11) NOT NULL,
            Path varchar(35) NOT NULL,
            UNIQUE KEY id (ID,Path(35)),
            INDEX (ID),
            INDEX (Path)
    )"""
    elif table == "MD5s":
        query = """CREATE TABLE MD5s (
            ID int(11) NOT NULL,
            MD varchar(35) NOT NULL,
            UNIQUE KEY id (ID,MD(35)),
            INDEX (ID),
            INDEX (MD)
    )"""
    elif table == "Provides":
        query = """CREATE TABLE Provides (
            ID int(11) NOT NULL,
            Resource varchar(35) NOT NULL,
            UNIQUE KEY id (ID,Resource(35)),
            INDEX (ID),
            INDEX (Resource)
    )"""
    elif table == "Requires":
        query = """CREATE TABLE Requires (
            ID int(11) NOT NULL,
            Resource varchar(35) NOT NULL,
            Rel char(2),
            Value varchar(20),
            UNIQUE KEY id (ID,Resource(35)),
            INDEX (ID),
            INDEX (Resource)
    )"""
    elif table == "Queries":
        query = """CREATE TABLE Queries (
            ID int(11) NOT NULL auto_increment,
            Value varchar(50) NOT NULL,
            Count int(11) NOT NULL,
            Results int(11) NOT NULL,
            UNIQUE KEY id (ID,Value(35)),
            INDEX (ID),
            INDEX (Value)
    )"""
    else:
        print("sql_rebuild_table: unknown table %s" % (table))
        return -1
    if do_sql_query(query) < 0:
        return -1
    print("rebuilt table %s" % (table))
    return 0

def sql_check_tables():
    if do_sql_query("SHOW TABLES") < 0:
        return -1
    rebuilt = 0
    list = cursor.fetchall()
    tables = ('Config', 'Distribs', 'Distributions', 'Files', 'Metadata',
              'Mirrors', 'Packages', 'Provides', 'Queries', 'Requires',
          'Vendors', 'MD5s', 'OldDistribs')
    for table in tables:
        found = 0
        for t in list:
            if t[0] == table:
                found = 1
                break
    if found == 0:
        print("Table %s missing" % (table))
        sql_rebuild_table(table)
        rebuilt = rebuilt + 1
    return rebuilt

#
# Additions
#

def sql_add_dist_mirror(distrib,URL,country):
    if URL == None:
        return -1
    if distrib < 0:
        return -1
    return sql_blind_insert("Mirrors", "URL", URL, distrib)

def sql_add_mirror(Name,URL,country):
    if Name == None or URL == None:
        return -1
    distrib = sql_read_key("Distribs", Name)
    if distrib < 0:
        return distrib
    return sql_blind_insert("Mirrors", "URL", URL, distrib)

def sql_add_md5(md5, package):
    if md5 == None or package <= 0:
        return -1
    if len(md5) > 35:
        return 0
    return sql_blind_insert("MD5s", "MD", md5, package)

def sql_add_file(filename, package):
    if filename == None or package <= 0:
        return -1
    if len(filename) > 35:
        return 0
    return sql_blind_insert("Files", "Path", filename, package)

def sql_add_requires(package,resource,rel,value):
    if resource == None or package <= 0:
        return -1
    if len(resource) > 35:
        return 0
    record = sql_blind_insert("Requires", "Resource", resource, package)
    if rel != None and value != None:
        if cursor == None:
            init_sql()
    try:
        cursor.execute("UPDATE Requires SET Rel='%s',Value='%s' WHERE ID=%d"
                       % (rel, value, record))
    except:
        print("sql_update: %s:%s failed to find id" % (table, name))
        print(sys.exc_info()[0], sys.exc_info()[1])
        return -1
    return record

def sql_add_vendor(Name,URL,Description):
    if Name == None:
        return -1
    id = sql_get_key("Vendors", "Name", Name)
    if id <= 0:
        id = sql_blind_insert("Vendors", "Name", Name, 0)
    if id <= 0:
        return id
    if URL != None:
        sql_update_id("Vendors", id, "URL", URL)
    if Description != None:
        sql_update_id("Vendors", id, "Description", Description)
    return id

def sql_add_distribution(Name, URL, Description):
    if Name == None:
        return -1
    id = sql_get_key("Distributions", "Name", Name)
    if id <= 0:
        id = sql_blind_insert("Distributions", "Name", Name, 0)
    if id <= 0:
        return id
    if URL != None:
        sql_update_id("Distributions", id, "URL", URL)
    if Description != None:
        sql_update_id("Distributions", id, "Description", Description)
    return id
#
# Deletion
#
def sql_delete_package(id):
    do_sql_query("DELETE FROM Packages WHERE ID='%d'" % (id))
    do_sql_query("DELETE FROM Files WHERE ID='%d'" % (id))
    do_sql_query("DELETE FROM Provides WHERE ID='%d'" % (id))
    do_sql_query("DELETE FROM Requires WHERE ID='%d'" % (id))
    do_sql_query("DELETE FROM MD5s WHERE ID='%d'" % (id))
    return 0

def sql_delete_distrib(path):
    id = int(sql_read_info_key('Distribs', 'Directory', path))
    if id == -1:
        return -1
    print("Removing distribution %s" % (path))
    do_sql_query("DELETE FROM Distribs WHERE Directory='%s'" % (path))
    do_sql_query("DELETE FROM Mirrors WHERE ID='%d'" % (id))
    do_sql_query("SELECT ID FROM Packages WHERE Dist='%d'" % (id))
    pkglist = list = cursor.fetchall();
    for id in pkglist:
        sql_delete_package(id)
    return 0

#
# Queries
#
queries = 0
def sql_get_package_id(filename):
    global queries
    id = sql_read_info_key('Packages', 'filename', filename)
    if id < 0:
        return id
    queries = queries + 1
    print("%d New package %s" % (queries, filename))
    return 0

def sql_get_top_queries(count):
    query = "select Value, Count from Queries order by count desc limit %d" % (
            count)
    if do_sql_query(query) < 0:
        return -1
    print("<queries>")
    result = cursor.fetchone()
    while result != None:
        if len(result) >= 2:
            print("<query occur='%d'>%s</query>" % (result[1], result[0]))
    result = cursor.fetchone()
    print("</queries>")
    return 0
        
#
# stats
#
def sql_show_table_stats(table,key):
    if do_sql_query("SELECT COUNT(%s) FROM %s" % (key, table))  < 0:
        return -1
    list = cursor.fetchone()
    if list[0] == 0:
        print("   %s is empty" % (table))
    else:
        print("   %s contains %d records" % (table, list[0]))
    return list[0]

def sql_show_stats():
    if do_sql_query("SHOW TABLES") < 0:
        return -1
    print("%d tables in use" % (len(cursor.fetchall())))
    records = 0
    records = records + sql_show_table_stats("Config", "Name")
    records = records + sql_show_table_stats("Distribs", "Name")
    records = records + sql_show_table_stats("Distributions", "Name")
    records = records + sql_show_table_stats("Vendors", "Name")
    records = records + sql_show_table_stats("Mirrors", "URL")
    records = records + sql_show_table_stats("Metadata", "URL")
    records = records + sql_show_table_stats("Packages", "Name")
    records = records + sql_show_table_stats("Requires", "Resource")
    records = records + sql_show_table_stats("Provides", "Resource")
    records = records + sql_show_table_stats("Files", "Path")
    records = records + sql_show_table_stats("MD5s", "ID")
    records = records + sql_show_table_stats("Queries", "ID")
    print("Total: %d records" % (records))
    
#
# Cleanup functions
#
def sql_remove_package(id):
    global cursor

    if cursor == None:
        init_sql()
    query = "DELETE FROM Packages WHERE ID=%d" % (id)
    if do_sql_query(query) < 0:
        return -1

    query = "DELETE FROM Files WHERE ID=%d" % (id)
    if do_sql_query(query) < 0:
        return -1
    
    query = "DELETE FROM Provides WHERE ID=%d" % (id)
    if do_sql_query(query) < 0:
        return -1
    
    query = "DELETE FROM Requires WHERE ID=%d" % (id)
    if do_sql_query(query) < 0:
        return -1

    query = "DELETE FROM MD5s WHERE ID=%d" % (id)
    if do_sql_query(query) < 0:
        return -1

def sql_check_packages():
    removed = 0
    if cursor == None:
        init_sql()
    # use a different cursor to be able to call do_sql_query()
    # when looking at the results
    mycursor = db.cursor()

    query = "SELECT filename,ID,Dist FROM Packages"
    if do_sql_query(query, mycursor) < 0:
        return -1
    row = mycursor.fetchone()
    while row != None:
        try:
            id = int(row[1])
        except:
            print("package %s bogus ID, removing it" % (row[0]))
            sql_remove_package(row[1])
            removed = removed + 1
            row = mycursor.fetchone()
            continue
        try:
            dist = int(row[2])
        except:
            print("package %s:%s bogus Dist, removing it" % (row[0], id))
            sql_remove_package(id)
            removed = removed + 1
            row = mycursor.fetchone()
            continue

        if row[0] == None or row[0] == '':
            print("package %s no filename, removing it" % (id))
            sql_remove_package(id)
            removed = removed + 1
        elif ("%s" % (dist) in sqlConfigById) == 0:
            print("package %s has no distrib, removing it" % (row[0]))
            sql_remove_package(id)
            removed = removed + 1
        elif row[0][0:9] != "localbase":
            try:
                os.stat(row[0])
                res = os.access(row[0], os.R_OK)
                if res == 0:
                    print("%s unreadable")
            except:
                print("%s disapeared, removing it from the database" % (row[0]))
                sql_remove_package(id)
                removed = removed + 1
                row = mycursor.fetchone()
    if removed != 0:
        print("Database cleanup : removed %d entries" % removed)
    return removed
    
def sql_remove_distrib(oldid):
    global cursor

    print("sql_remove_distrib(%d)" % (oldid))
    if cursor == None:
        init_sql()
    mycursor = db.cursor()
    query = "SELECT Name, Vendor, Directory, Path, URL, URLSrc, Html, Color, Key1, Key2, Description FROM Distribs where ID=%d" % (oldid)
    if do_sql_query(query, mycursor) < 0:
        print("sql_remove_distrib: cannot find distrib %d" % (oldid))
        return -1
    row = mycursor.fetchone()
    if row == None:
        print("sql_remove_distrib: cannot get distrib %d infos" % (oldid))
        return
    id = sql_get_key("OldDistribs", "Name", row[0])
    if id <= 0:
        print("sql_remove_distrib: failed to create %s in OldDistribs" % (row[0]))
        return

    if row[1] != None:
        sql_update_id("OldDistribs", id, "Vendor", row[1])
    if row[2] != None:
        sql_update_id("OldDistribs", id, "Directory", row[2])
    if row[3] != None:
        sql_update_id("OldDistribs", id, "Path", row[3])
    if row[4] != None:
        sql_update_id("OldDistribs", id, "URL", row[4])
    if row[5] != None:
        sql_update_id("OldDistribs", id, "URLSrc", row[5])
    if row[6] != None:
        sql_update_id("OldDistribs", id, "Html", row[6])
    if row[7] != None:
        sql_update_id("OldDistribs", id, "Color", row[7])
    if row[8] != None:
        sql_update_id("OldDistribs", id, "Key1", row[8])
    if row[9] != None:
        sql_update_id("OldDistribs", id, "Key2", row[9])
    if row[10] != None:
        sql_update_id("OldDistribs", id, "Description", row[10])
    query = "DELETE FROM Distribs where ID=%d" % (oldid)
    if do_sql_query(query) < 0:
        return -1


def sql_check_distribs():
    removed = 0
    if cursor == None:
        init_sql()
    mycursor = db.cursor()

    query = "SELECT Directory,ID FROM Distribs"
    if do_sql_query(query, mycursor) < 0:
        return -1
    row = mycursor.fetchone()
    while row != None:
        try:
            os.stat(row[0])
            res = os.access(row[0], os.R_OK)
            if res == 0:
                print("%s unreadable")
        except:
            print("%s disapeared, moving it" % (row[0]))
            sql_remove_distrib(int(row[1]))
            removed = removed + 1
        row = mycursor.fetchone()
    if removed != 0:
        print("Database cleanup : removed %d distributions" % removed)
    return removed
    
#
# Integrity checks
#
def sql_cleanup_tables():
    global cursor

    query = "SELECT ID from Packages ORDER BY ID ASC"
    if do_sql_query(query) < 0:
        return -1
    pkgIDs = cursor.fetchall()
    lpkgIDs = len(pkgIDs)

    #
    # Check the Requires against the Packages IDs
    #
    print("Checking Requires")
    query = "SELECT DISTINCT ID from Requires ORDER BY ID ASC"
    if do_sql_query(query) < 0:
        return -1
    reqIDs = cursor.fetchall()
    lreqIDs = len(reqIDs)
    pkg = 0
    req = 0
    dropped = 0
    while pkg < lpkgIDs and req < lreqIDs:
        curPkg = int(pkgIDs[pkg][0])
    while req < lreqIDs:
        curReq = int(reqIDs[req][0])
        if curReq < curPkg:
            do_sql_query("DELETE QUICK FROM Requires WHERE ID=%d" % (curReq))
            dropped = dropped + 1
            req = req + 1
        elif curReq == curPkg:
            req = req + 1
        else:
            break;
        pkg = pkg + 1
    while req < lreqIDs:
        curReq = int(reqIDs[req][0])
        do_sql_query("DELETE QUICK FROM Requires WHERE ID=%d" % (curReq))
        dropped = dropped + 1
        req = req + 1
    if dropped > 0:
        print("Dropped %d ID Requires" % (dropped))
    del reqIDs
    
    #
    # Check the Provides against the Packages IDs
    #
    print("Checking Provides")
    query = "SELECT DISTINCT ID from Provides ORDER BY ID ASC"
    if do_sql_query(query) < 0:
        return -1
    proIDs = cursor.fetchall()
    lproIDs = len(proIDs)
    pkg = 0
    pro = 0
    dropped = 0
    while pkg < lpkgIDs and pro < lproIDs:
        curPkg = int(pkgIDs[pkg][0])
        while pro < lproIDs:
            curPro = int(proIDs[pro][0])
            if curPro < curPkg:
                do_sql_query("DELETE QUICK FROM Provides WHERE ID=%d" % (curPro))
                dropped = dropped + 1
                pro = pro + 1
            elif curPro == curPkg:
                pro = pro + 1
            else:
                break;
        pkg = pkg + 1
        while pro < lproIDs:
            curPro = int(proIDs[pro][0])
            do_sql_query("DELETE QUICK FROM Provides WHERE ID=%d" % (curPro))
            dropped = dropped + 1
            pro = pro + 1
    if dropped > 0:
        print("Dropped %d ID Provides" % (dropped))
    del proIDs
    
    #
    # Check the Files against the Packages IDs
    #
    print("Checking Files")
    query = "SELECT DISTINCT ID from Files ORDER BY ID ASC"
    if do_sql_query(query) < 0:
        return -1
    filIDs = cursor.fetchall()
    lfilIDs = len(filIDs)
    pkg = 0
    fil = 0
    dropped = 0
    while pkg < lpkgIDs and fil < lfilIDs:
        curPkg = int(pkgIDs[pkg][0])
        while fil < lfilIDs:
            curFil = int(filIDs[fil][0])
            if curFil < curPkg:
                do_sql_query("DELETE QUICK FROM Files WHERE ID=%d" % (curFil))
                dropped = dropped + 1
                fil = fil + 1
            elif curFil == curPkg:
                fil = fil + 1
            else:
                break;
        pkg = pkg + 1
        while fil < lfilIDs:
            curFil = int(filIDs[fil][0])
            do_sql_query("DELETE QUICK FROM Files WHERE ID=%d" % (curFil))
            dropped = dropped + 1
            fil = fil + 1
    if dropped > 0:
        print("Dropped %d ID Files" % (dropped))
    del filIDs

    #
    # Check the MD5s against the Packages IDs
    #
    print("Checking MD5s")
    query = "SELECT DISTINCT ID from MD5s ORDER BY ID ASC"
    if do_sql_query(query) < 0:
        return -1
    md5IDs = cursor.fetchall()
    lmd5IDs = len(md5IDs)
    pkg = 0
    md5 = 0
    dropped = 0
    while pkg < lpkgIDs and md5 < lmd5IDs:
        curPkg = int(pkgIDs[pkg][0])
        while md5 < lmd5IDs:
            curMd5 = int(md5IDs[md5][0])
            if curMd5 < curPkg:
                do_sql_query("DELETE QUICK FROM MD5s WHERE ID=%d" % (curMd5))
                dropped = dropped + 1
                md5 = md5 + 1
            elif curMd5 == curPkg:
                md5 = md5 + 1
            else:
                break;
        pkg = pkg + 1
        while md5 < lmd5IDs:
            curMd5 = int(md5IDs[md5][0])
        do_sql_query("DELETE QUICK FROM MD5s WHERE ID=%d" % (curMd5))
        dropped = dropped + 1
        md5 = md5 + 1
    if dropped > 0:
        print("Dropped %d ID MD5s" % (dropped))
    del md5IDs
    del lpkgIDs
    
#
# Insert the config file into the database
#
def sqlConfigEntry(rpmdir, name, value):
    global rpm2htmlVerbose
    
    if rpm2htmlVerbose > 1:
        print("sqlConfigEntry(%s, %s, %s)\n" % (rpmdir, name, value))

    #
    # case of global option for rpm2html.
    #
    if rpmdir == "rpm2html":
        sql_add_config_info(name, value)

    #
    # Options for the metadata mirrors.
    #
    if rpmdir == "metadata":
        if name == "mirror":
            sql_add_metadata_base(value)
        else:
            print("Config file : %s entry for [metadata] ignored\n" % (name))


    #
    # option for a directory.
    #
    if name == "name":
        sql_add_distrib(value, None, rpmdir, None, None, None, None, None, None)
    elif name == "subdir":
        distrib = sql_read_info_key("Distribs", "Directory", rpmdir)
        if distrib > 0:
            sql_update_id("Distribs", distrib, "Path", value)
        else:
            print("database has no distrib: %s" % (rpmdir))
    elif name == "url":
        distrib = sql_read_info_key("Distribs", "Directory", rpmdir)
        if distrib > 0:
            sql_update_id("Distribs", distrib, "URL", value)
        else:
            print("database has no distrib: %s" % (rpmdir))
    elif name == "ftp":
        distrib = sql_read_info_key("Distribs", "Directory", rpmdir)
        if distrib > 0:
            sql_update_id("Distribs", distrib, "URL", value)
        else:
            print("database has no distrib: %s" % (rpmdir))
    elif name == "ftpsrc":
        distrib = sql_read_info_key("Distribs", "Directory", rpmdir)
        if distrib > 0:
            sql_update_id("Distribs", distrib, "URLSrc", value)
        else:
            print("database has no distrib: %s" % (rpmdir))
    elif name == "html":
        distrib = sql_read_info_key("Distribs", "Directory", rpmdir)
        if distrib > 0:
            sql_update_id("Distribs", distrib, "Html", value)
        else:
            print("database has no distrib: %s" % (rpmdir))
    elif name == "color":
        distrib = sql_read_info_key("Distribs", "Directory", rpmdir)
        if distrib > 0:
            sql_update_id("Distribs", distrib, "Color", value)
        else:
            print("database has no distrib: %s" % (rpmdir))
    elif name == "mirror":
        distrib = sql_read_info_key("Distribs", "Directory", rpmdir)
        if distrib > 0:
            sql_add_dist_mirror(distrib, value, 0)
        else:
            print("database has no distrib: %s" % (rpmdir))
    else:
        print("Config file : %s entry for [%s] ignored\n" % (name, rpmdir))


def sql_add_config_info(name, value):
    sql_update("Config", name, "Value", value)

def sql_add_metadata_base(URL):
    sql_blind_insert("Metadata", "URL", URL, -1)


def sql_add_distrib(Name, Vendor, Directory, Path, URL, URLSrc, Description, Html, Color):
    nb_fields = 0
    if Name == None:
        return-1

    id = sql_get_key("Distribs", "Name", Name)
    nb_fields = 1;
    if Vendor is not None:
        vendor = sql_get_key("Vendors", "Name", Vendor)
        #TODO:
        #Figure out VendorStr value from vendor
        VendorStr = vendor
        nb_fields += sql_update_id("Distribs", id, "Vendor", VendorStr)
    if Directory is not None:
        nb_fields += sql_update_id("Distribs", id, "Directory", Directory)
    if Path is not None:
        nb_fields += sql_update_id("Distribs", id, "Path", Path)
    if URL is not None:
        nb_fields += sql_update_id("Distribs", id, "URL", URL)
    if URLSrc is not None:
        nb_fields += sql_update_id("Distribs", id, "URLSrc", URLSrc)
    if Html is not None:
        nb_fields += sql_update_id("Distribs", id, "Html", Html)
    if Color is not None:
        nb_fields += sql_update_id("Distribs", id, "Color", Color)
    if Description is not None:
        nb_fields += sql_update_id("Distribs", id, "Description", Description)
    return(nb_fields);


if __name__ == "__main__":
    sql_check_tables()
    sql_show_stats()
    sql_cleanup_tables()
    sql_show_stats()

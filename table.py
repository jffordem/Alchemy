#!/usr/bin/env python
__copyright__ = """
Copyright (c) Hewlett-Packard Company, 2015
 
All rights are reserved.  Copying or other reproduction of this
program except for archival purposes is prohibited without the prior
written consent of Hewlett-Packard Company.
 
RESTRICTED RIGHTS LEGEND
 
Use, duplication, or disclosure by the Government is subject to
restrictions as set forth in paragraph (b) (3) (B) of the Rights in
Technical Data and Computer Software clause in DAR 7-104.9(a).

HEWLETT-PACKARD COMPANY
11311 Chinden Boulevard
Boise, Idaho    83714
"""

__doc__ = """
Table.py is a table writing abstraction to emit tabular data in an attractive format.

Table is an interface (yes, I know Python doesn't have interfaces, so maybe it's an archetype) that
the TableFormat uses to format the data.

TableFormat is an interface (yes, I heard you the first time!) that emits table rows in the desired
format.

Table
    headers(self) must return array of header strings, like [ 'name', 'title', 'phone' ]
    rows(self) must return a dictionary for each row, like [ { 'name': 'fred', 'title': 'director', 'phone': '123-4556' }, { 'name', 'barney', 'title': 'key grip', 'phone': '123-5678' }, ... ]
    
TableFormat
    printOuterBorderRow(self, widths, columns)
    printHeadersRow(self, widths, columns)
    printHeaderSeperatorRow(self, widths, columns)
    printDataRow(self, widths, columns, values)
"""

import csv

def matchAll(row, args):
    #print("matching", row, 'with', args)
    for k,v in args.items():
        if row[k] != v: 
            #print("didn't match because", k, v, "didn't match", row)
            return False
    #print("matched", row, "with", args)
    return True

class Table:
    def __init__(self, headers, rows, sortby = None):
        if headers == None: headers = [ ]
        self.__headers = list(headers)
        self.__rows = list(rows)
        self.__sortby = sortby
    def setSortCol(self, sortby):
        self.__sortby = sortby
    def headers(self): return self.__headers
    def rows(self):
        if self.__sortby != None:
            reverse = False
            if self.__sortby.startswith("+"): 
                self.__sortby = self.__sortby[1:]
            if self.__sortby.startswith("-"): 
                self.__sortby = self.__sortby[1:]
                reverse = True
            self.__rows = sorted(self.__rows, key=lambda row: row[self.__sortby], reverse=reverse)
            self.__sortby = None
        return self.__rows
    def select(self, **eqargs):
        return [ row for row in self.rows() if matchAll(row, eqargs) ]
    def find(self, **eqargs):
        selected = self.select(**eqargs)
        if len(selected) > 0: return selected[0]
        return None
    def __len__(self): return len(self.__rows)
    @staticmethod
    def parseCsv(text, sep=',', sortby=None):
        if text == None: return None
        return Table._processCsv(text.split("\n"), sep, sortby)
    @staticmethod
    def readCsv(file, sep=',', sortby=None):
        with open(file, 'r') as f:
            return Table._processCsv(f, sep, sortby)
    @staticmethod
    def _processCsv(lines, sep, sortby):
        reader = csv.reader(lines, delimiter=sep)
        header = None
        rows = [ ]
        for line in reader:
            if line == None or len(line) == 0: continue
            if header == None:
                header = line
            else:
                rows.append({ header[i]: line[i] for i in range(len(header)) })
        return Table(header, rows, sortby)

def getValue(d, k):
    if k in d.keys():
        return d[k]
    return " "

class HtmlTableFormat:
    def __init__(self, style = None):
        self.__style = style
        self.__buffer = ""
    def startTable(self):
        if self.__style == None:
            self.__buffer += "<table>"
        else:
            self.__buffer += "<table style="+self.__style+">"
    def endTable(self):
        self.__buffer += "</table>"
    def printOuterBorderRow(self, widths, columns):
        pass
    def printHeadersRow(self, widths, columns):
        self.__buffer += "<tr>" + "".join([ "<th>"+col+"</th>" for col in columns ]) + "</tr>"
    def printHeaderSeperatorRow(self, widths, columns):
        pass
    def printDataRow(self, widths, columns, values):
        self.__buffer += "<tr>" + "".join([ "<td>"+str(getValue(values, col))+"</td>" for col in columns ]) + "</tr>"
    def __repr__(self): return self.__buffer

class BorderTableFormat:
    def __init__(self, corner = "+", vert = "|", horz = "-"):
        self.__corner = corner
        self.__vert = vert
        self.__horz = horz
    def printOuterBorderRow(self, widths, columns):
        print(self.__corner + self.__corner.join( [ "-" * widths[col] for col in columns ] ) + self.__corner)
    def printHeadersRow(self, widths, columns):
        print(self.__vert + self.__vert.join( [ col.center(widths[col]) for col in columns ] ) + self.__vert)
    def printHeaderSeperatorRow(self, widths, columns):
        self.printOuterBorderRow(widths, columns)
    def printDataRow(self, widths, columns, values):
        print(self.__vert + self.__vert.join( [ str(getValue(values, col)).ljust(widths[col]) for col in columns ] ) + self.__vert)
    def startTable(self):
        pass
    def endTable(self):
        pass

class DefaultTableFormat:
    def __init__(self, horz = "="):
        self.__horz = horz
        self.__format = format
    def printOuterBorderRow(self, widths, columns):
        print()
    def printHeadersRow(self, widths, columns):
        print(" ".join( [ col.center(widths[col]) for col in columns ] ))
    def printHeaderSeperatorRow(self, widths, columns):
        print(" ".join( [ self.__horz * widths[col] for col in columns ] ))
    def printDataRow(self, widths, columns, values):
        print(" ".join( [ str(getValue(values, col)).ljust(widths[col]) for col in columns ] ))
    def startTable(self):
        pass
    def endTable(self):
        pass

def printTable(table, format = DefaultTableFormat()):
    def getWidths(rows):
        result = { k: len(k) for k in rows[0].keys() }
        for row in rows:
            for col in row.keys():
                if col in result.keys():
                    result[col] = max(len(str(getValue(row, col))), result[col])
                else:
                    result[col] = len(str(getValue(row, col)))
        return result
    if table != None and len(table) > 0:
        columns = table.headers()
        rows = table.rows()
        widths = getWidths(rows)
        format.startTable()
        format.printOuterBorderRow(widths, columns)
        format.printHeadersRow(widths, columns)
        format.printHeaderSeperatorRow(widths, columns)
        for row in rows:
            format.printDataRow(widths, columns, row)
        format.printOuterBorderRow(widths, columns)
        format.endTable()
        
if __name__ == "__main__":
    printTable(Table([ 'a', 'b', 'c' ], [ 
    { 'a': 1, 'b': 2.0, 'c': { 1, 2 } }, 
    { 'a': "Hello", 'b': complex(1, 2), 'c':None },
    { 'a': { 'p':1, 'q':2 }, 'b': (1,2,3) },
    { 'c': "Fred" },
    ]))

    printTable(Table.parseCsv("""a,b,c
1,2,3
4,5,6"""))

    fmt = HtmlTableFormat()
    printTable(Table.parseCsv("""a,b,c
4,5,6
1,2,3""", sortby='a'), fmt)
    print(str(fmt))

    #printTable(Table.readCsv("sf_jobs.csv"))
    
    printTable(Table.parseCsv("""a\tb\tc
1\t2\t3
4\t5\t6

""", '\t'))

    table = Table.parseCsv("""a,b,c
1,2,3
4,5,6""")
    if table.select(a='1') != [ { 'a':'1', 'b':'2', 'c':'3' } ]:
        print("Select FAILED returned", table.select(a='1'))

    if table.select(a='1', b='2') != [ { 'a':'1', 'b':'2', 'c':'3' } ]:
        print("Select FAILED returned", table.select(a='1', b='2'))

    if table.find(a='1') != { 'a':'1', 'b':'2', 'c':'3' }:
        print("Find FAILED returned", table.find(a='1'))
    
    printTable(Table.parseCsv(None))
    printTable(Table.parseCsv(""))
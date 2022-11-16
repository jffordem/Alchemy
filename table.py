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

Examples:
- load and print table from csv file
    from table import Table, printTable
    data = Table.readCsv(filename)
    printTable(data)

Query Language
    stuff = Table.readCsv(filename).where(sourceOrderId="12345678").sort(timestamp=1)
    printTable(stuff)
"""

import csv
import json

def matchAll(row, args):
    for k,v in args.items():
        if row[k] != v: 
            return False
    return True

def matchAllp(row, preds):
    return all([ pred(row) for pred in preds ])

class Table:
    def __init__(self, headers, rows):
        if headers == None: headers = [ ]
        self.__headers = list(headers)
        self.__rows = list(rows)
    def headers(self): return self.__headers
    def rows(self): return self.__rows
    def select(self, **eqargs):
        return [ row for row in self.rows() if matchAll(row, eqargs) ]
    def selectp(self, *preds):
        return [ row for row in self.rows() if matchAllp(row, preds) ]
    def where(self, **args):
        result = Table(self.__headers, self.__rows)
        result.__rows = result.select(**args)
        return result
    def wherep(self, *preds):
        result = Table(self.__headers, self.__rows)
        result.__rows = result.selectp(*preds)
        return result
    def find(self, **eqargs):
        selected = self.select(**eqargs)
        if len(selected) > 0: return selected[0]
        return None
    def sort(self, column, reverse=False):
        self.__rows = sorted(self.__rows, key=lambda row: row[column], reverse=reverse)
        return self
    def limit(self, count=10):
        self.__rows = self.__rows[:count]
        return self
    def addColumn(self, name, values):
        self.__headers.append(name)
        for row, value in zip(self.__rows, values):
            row[name] = value
    def __len__(self): return len(self.__rows)
    def __iter__(self): return iter(self.__rows)
    def __add__(self, other):
        if self.headers() == other.headers():
            return Table(self.headers(), self.rows() + other.rows())
        return None
    def writeCsv(self, file, sep=','):
        with open(file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.__headers)
            writer.writeheader()
            for row in self.__rows:
                writer.writerow(row)
    def writeJson(self, file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dumps(self.__rows)
    @staticmethod
    def parseCsv(text, sep=','):
        if text == None: return None
        return Table._processCsv(text.split("\n"), sep)
    @staticmethod
    def readCsv(file, sep=','):
        with open(file, 'r') as f:
            return Table._processCsv(f, sep)
    @staticmethod
    def readJson(file):
        with open(file, 'r', encoding='utf-8') as f:
            rows = json.load(f)
            headers = set()
            for row in rows:
                for key in row.keys():
                    headers.add(key)
            return Table(headers, rows)
    def parseFixed(lines, hasCaption=False):
        def getHeaderCols(line):
            inWord = False
            lastStart = -1
            result = dict()
            headers = []
            for i in range(len(line)):
                if not inWord and line[i] != ' ':
                    if lastStart >= 0:
                        header = line[lastStart:i].strip()
                        result[header] = (lastStart, i)
                        headers.append(header)
                    lastStart = i
                    inWord = True
                elif inWord and line[i] == ' ':
                    inWord = False
            header = line[lastStart:len(line)-1].strip()
            result[header] = (lastStart, len(line)-1)
            headers.append(header)
            return headers, result
        def getField(line, headerCols):
            return line[headerCols[0]:headerCols[1]].strip().rstrip('-').strip()
        def isSeparator(line):
            for field in line.split():
                if len(field.strip('-')) != 0:
                    return False
            return True
        caption = []
        if hasCaption: caption = None
        headers = None
        headerCols = None
        rows = []
        for line in lines:
            if len(line.strip()) == 0 or isSeparator(line): continue
            fields = line.strip().split()
            if len(fields) == 0: continue
            if caption == None: caption = fields
            elif headers == None: headers, headerCols = getHeaderCols(line)
            else: rows.append({ column: getField(line, headerCols[column]) for column in headers })
        return Table(headers, rows)
    @staticmethod
    def readFixed(file, hasCaption=False):
        with open(file, 'r', encoding='utf-8') as f:
            return Table.parseFixed(f)
    @staticmethod
    def _processCsv(lines, sep):
        reader = csv.reader(lines, delimiter=sep)
        header = None
        rows = [ ]
        for line in reader:
            if line == None or len(line) == 0: continue
            if header == None:
                header = line
            else:
                rows.append({ header[i]: line[i] for i in range(len(header)) })
        return Table(header, rows)
    @staticmethod
    def fromCursor(cursor):
        def toDictionary(cols, rows):
            for row in rows:
                yield { k: v for k, v in zip(cols, row) }
        cols = [ col[0] for col in cursor.description ]
        return Table(cols, toDictionary(cols, cursor.fetchall()))

def getValue(d, k):
    if k in d.keys():
        return d[k]
    return " "

class BorderTableFormat:
    def __init__(self, corner = "+", vert = "|", horz = "-"):
        self.__corner = corner
        self.__vert = vert
        self.__horz = horz
    def printStartTable(self):
        pass
    def printEndTable(self):
        pass
    def printOuterBorderRow(self, widths, columns):
        print(self.__corner + self.__corner.join( [ "-" * widths[col] for col in columns ] ) + self.__corner)
    def printHeadersRow(self, widths, columns):
        print(self.__vert + self.__vert.join( [ col.center(widths[col]) for col in columns ] ) + self.__vert)
    def printHeaderSeperatorRow(self, widths, columns):
        self.printOuterBorderRow(widths, columns)
    def printDataRow(self, widths, columns, values):
        print(self.__vert + self.__vert.join( [ str(getValue(values, col)).ljust(widths[col]) for col in columns ] ) + self.__vert)

class DefaultTableFormat:
    def __init__(self, horz = "="):
        self.__horz = horz
        self.__format = format
    def printStartTable(self):
        pass
    def printEndTable(self):
        pass
    def printOuterBorderRow(self, widths, columns):
        print()
    def printHeadersRow(self, widths, columns):
        print(" ".join( [ col.center(widths[col]) for col in columns ] ))
    def printHeaderSeperatorRow(self, widths, columns):
        print(" ".join( [ self.__horz * widths[col] for col in columns ] ))
    def printDataRow(self, widths, columns, values):
        print(" ".join( [ str(getValue(values, col)).ljust(widths[col]) for col in columns ] ))

def printTable(table, writer = DefaultTableFormat()):
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
        writer.printStartTable()
        writer.printOuterBorderRow(widths, columns)
        writer.printHeadersRow(widths, columns)
        writer.printHeaderSeperatorRow(widths, columns)
        for row in rows:
            writer.printDataRow(widths, columns, row)
        writer.printOuterBorderRow(widths, columns)
        writer.printEndTable()

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
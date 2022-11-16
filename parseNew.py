import table
from table import Table, printTable
import re
import sys

def parseEffect(effect):
    def parseModifiers(name, mods):
        mag = val = '1'
        fields = mods.split(',')
        for field in fields:
            if field.endswith('-Magnitude'):
                mag = field[:-len('-Magnitude')]
            if field.endswith('-Value'):
                val = field[:-len('-Value')]
        return (name, mag, val)
    one = r'(\b\S+\b)\s+\b\1\b'
    oneParen = r'(\b\S+\b)\s+\b\1\b\s+\((\S+)\)'
    two = r'(\b\S+\b)\s+(\b\S+\b)\s+\b\1\b\s+\b\2\b'
    twoParen = r'(\b\S+\b)\s+(\b\S+\b)\s+\b\1\b\s+\b\2\b\s+\((\S+)\)'
    three = r'(\b\S+\b)\s+(\b\S+\b)\s+(\b\S+\b)\s+\b\1\b\s+\b\2\b\s+\b\3\b'
    threeParen = r'(\b\S+\b)\s+(\b\S+\b)\s+(\b\S+\b)\s+\b\1\b\s+\b\2\b\s+\b\3\b\s+\((\S+)\)'
    match = re.match(threeParen, effect)
    if match:
        return parseModifiers(match[1] + ' ' + match[2] + ' ' + match[3], match[4])
    match = re.match(three, effect)
    if match:
        return (match[1] + ' ' + match[2] + ' ' + match[3], '1', '1')
    match = re.match(twoParen, effect)
    if match:
        return parseModifiers(match[1] + ' ' + match[2], match[3])
    match = re.match(two, effect)
    if match:
        return (match[1] + ' ' + match[2], '1', '1')
    match = re.match(oneParen, effect)
    if match:
        return parseModifiers(match[1], match[2])
    match = re.match(one, effect)
    if match:
        return (match[1], '1', '1')
    raise Exception(f'could not parse {effect}')

if __name__ == '__main__':
    with open('temp-new-ones.txt') as f:
        headers = 'name,weight,value,effect_1_name,effect_1_power,effect_1_value,effect_2_name,effect_2_power,effect_2_value,effect_3_name,effect_3_power,effect_3_value,effect_4_name,effect_4_power,effect_4_value'.split(',')
        rows = []
        row = dict()
        state = 'start'
        for line in f:
            if len(line.strip()) == 0: continue
            fields = line.split('\t')
            if len(fields) == 2 and fields[0].endswith('.png'):
                if len(row) > 0:
                    rows.append(row)
                row = dict()
                row['name'] = fields[1].strip()
                state = 'name'
            elif state == 'name':
                #if len(fields) == 1:
                #    row['description'] = fields[0]
                #elif len(fields) == 2:
                #    row['description'] = fields[1]
                state = 'description'
            elif state == 'description':
                row['effect_1_name'], row['effect_1_power'], row['effect_1_value'] = parseEffect(fields[0])
                row['effect_2_name'], row['effect_2_power'], row['effect_2_value'] = parseEffect(fields[1])
                row['effect_3_name'], row['effect_3_power'], row['effect_3_value'] = parseEffect(fields[2])
                row['effect_4_name'], row['effect_4_power'], row['effect_4_value'] = parseEffect(fields[3])
                row['value'] = fields[4]
                row['weight'] = fields[5]
                state = 'start'
        if len(row) > 0:
            rows.append(row)

    t = Table(headers, rows)
    #printTable(t)
    t.writeCsv('temp-new-ones.csv')

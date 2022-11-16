import json

uesp = 'https://en.uesp.net/wiki/Skyrim:{name}'

with open('alchemyData.json') as fi:
    data = json.load(fi)
    effects = data['effects']
    for effect in effects:
        effect['link'] = uesp.format(name=effect['name'].replace(' ', '_'))
        #print(effect['name'], effect['link'])
        with open('alchemyData2.json', 'w') as fo:
            json.dump(data, fo)
    print('saved changes to', 'alchemyData2.json')

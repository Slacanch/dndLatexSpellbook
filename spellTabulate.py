import sys
import json
import argparse
from tabulate import tabulate
from operator import itemgetter

#functions
def findRitual(spellDict):
    if spellDict['ritual']:
        return "yes"
    else:
        return "-"

def findHigherLevels(spellDict):
    if 'higher_levels' in spellDict:
        return spellDict['higher_levels']
    else:
        return("-")


def findAttack(description):
    attackSignatures = {'make a melee spell attack' : 'melee',
                        'make a ranged spell attack': 'ranged', }

    for signature in attackSignatures.keys():
        if signature in description.lower():
            return attackSignatures[signature]

    return '-'

def findSave(description):
    throwSignatures = { 'dexterity saving throw' : 'dex',
                        'wisdom saving throw': 'wis',
                        'charisma saving throw' : 'cha',
                        'strength saving throw': 'str',
                        'constitution saving throw': 'con',
                        'intelligence saving throw': 'int', }

    for signature in throwSignatures.keys():
        if signature in description.lower():
            return throwSignatures[signature]

    return '-'

def readSpells():
    with open('spells.json', 'rb') as spellsFile:
        allSpells = json.load(spellsFile)
        dictSpells = {}
        for spell in allSpells:
            dictSpells[spell['name'].lower()] = spell
        return dictSpells


#options
options = argparse.ArgumentParser(description = 'make nice spell lists in pdf format',
                                  formatter_class = argparse.ArgumentDefaultsHelpFormatter)
options.add_argument("spellBook",
                     help =  "File containing spells in your spellbook, ordered by level")
args = options.parse_args()

allSpells = readSpells()

with open(args.spellBook, 'r') as spellBook:
    tablesDict = {}
    header = ['Name', 'School', 'Cast Time', 'Range', 'Duration',
             'Save Throw', 'Attack', 'Ritual' , 'Description', 'Higher Levels']

    for spellName in spellBook:
        spellName = spellName.strip().lower()
        try:
            currentSpell = allSpells[spellName]
        except KeyError:
            print(f"information about {spellName} is not included in my list, add it!")
            sys.exit()

        #check for table existance or create one
        level = currentSpell['level']
        if level in tablesDict:
            pass
        else:
            tablesDict[level] = []

        #fill Table
        requiredFields = ['school', 'casting_time', 'range',
                          'duration', 'description']
        school, castTime, spellRange, duration, description = [currentSpell[x] for x in requiredFields]
        saves = findSave(description)
        attack = findAttack(description)
        higherLevels = findHigherLevels(currentSpell)
        ritual = findRitual(currentSpell)
        description = description.replace("\n", "")

        tablesDict[level].append([spellName.capitalize(), school, castTime, spellRange,
                      duration, saves, attack, ritual, description, higherLevels])


#generating tables
latexDict = {}
for level in ['cantrip', '1', '2', '3', '4', '5', "6", "7", "8", "9"]:
    if level in tablesDict:
        sortedTable = sorted(tablesDict[level], key = itemgetter(0))
        latexDict[level] = tabulate(sortedTable, headers= header, tablefmt= 'latex')


#formatting latex document
finalLatex = ""
preamble = ("\\documentclass[a4paper]{article}\n"
            "\\usepackage{lscape}\n"
            "\\usepackage[left=0.5cm, right=0.5cm, top=0.5cm, bottom=0.5cm]{geometry}\n"
            "\\usepackage{longtable}\n"
            "\\begin{document}\n"
            "\\begin{landscape}\n")
finalLatex += preamble

for level in latexDict:
    if level == 'cantrip':
        finalLatex += "\\center{\\Large {\\bf Cantrips}}\n\n"
    else:
        finalLatex += f"\\center{{\\Large {{\\bf Level {level}}}}}\n\n"

    tabular = latexDict[level]
    tabularList = tabular.split("\n")
    #changing positioning
    tabularList[0] = "\\begin{longtable}{p{0.7in}p{0.75in}p{0.5in}p{0.5in}p{0.5in}cccp{3.2in}p{1.65in}}\n"
    tabularList[1] = ''
    tabularList[len(tabularList)-2] = ""
    tabularList[len(tabularList)-1] = "\\end{longtable}"

    for i in range(4, len(tabularList) - 2):
        spellLine = tabularList[i]
        spellLineList = spellLine.split("&")

        #name line
        spellLineList[0] = "\\textbf{" + spellLineList[0].strip() + "}"
        #description line
        spellLineList[8] = "\\scriptsize{" + spellLineList[8].strip() + "}"
        #higher levels line, must add backslashes because this is the last element of each row
        spellLineList[9] = spellLineList[9].replace("\\",'')
        spellLineList[9] = "\\scriptsize{" + spellLineList[9].strip() + "}" + " \\\\"

        tabularList[i] = "&".join(spellLineList)

    finalLatex += "\n".join(tabularList) + "\n\n"

finalLatex += "\end{landscape}\n"

#tabella riassuntiva

finalLatex += "\clearpage\n"

for level in ['cantrip', '1', '2', '3', '4', '5', "6", "7", "8", "9"]:
    if level in tablesDict:
        sortedTable = sorted([x[0] for x in tablesDict[level]])

        finalLatex += ""






finalLatex += "\end{document}"
print(finalLatex)
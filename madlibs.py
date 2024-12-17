import random
from typing import Optional
import yaml
import argparse
from pydantic import BaseModel

__doc__ = """
This module provides a simple madlib generator.  It is used by the Flask app to generate random text for the user to enjoy.
This version doesn't require the text to be a data structure.  It just requires alternate clauses to be in parens and separated by a slash.
"""

class Madlib(BaseModel):
    """A madlib is a simple game where you fill in the blanks with random words.  The text is a string with alternate clauses in parens separated by a slash."""
    name: str
    text: str
    ref: Optional[str]

    def render(self) -> list[str]:
        return (
            _all(self.text)
                .replace("\r", "")
                .replace("  ", " ")
                .split('\n')
        )
    
    @staticmethod
    def from_dict(data: dict) -> 'Madlib':
        return Madlib(**data)
    
    @staticmethod
    def from_file(filename: str = "madlibs.yaml") -> list['Madlib']:
        if filename.endswith(".yaml"):
            return [Madlib.from_dict(item) for item in yaml.safe_load(open(filename, "r"))]
        else:
            raise ValueError("Unsupported file type")


AllMadlibsByName = {
    item.name: item
    for item in Madlib.from_file()
}


def _all(s):
    result = ""
    temp = ""
    i = 0
    for ch in s:
        if i == 0 and ch == '(':
            i += 1
        elif i == 1 and ch == ')':
            i -= 1
            result += _any(temp)
            temp = ""
        elif ch == '(':
            i += 1
            temp += ch
        elif ch == ')':
            i -= 1
            temp += ch
        elif i == 0:
            result += ch
        else:
            temp += ch
    return result

def _any(s):
    result = [ ]
    temp = ""
    i = 0
    for ch in s:
        if ch == '(':
            temp += ch
            i += 1
        elif ch == ')':
            temp += ch
            i -= 1
        elif i == 0 and ch == '/':
            result.append(_all(temp))
            temp = ""
        else:
            temp += ch
    if len(temp) > 0:
        result.append(_all(temp))
    return random.choice(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("madlib", help="The name of the madlib to generate, or __list to list all madlibs.")
    args = parser.parse_args()
    if args.madlib == "__list":
        print("\n".join(AllMadlibsByName.keys()))
    elif args.madlib in AllMadlibsByName:
        madlib = AllMadlibsByName[args.madlib].render()
        print("\n".join(madlib))
    else:
        print(f"Madlib '{args.madlib}' not found.")

#Skeleton Program code for the AQA A Level Paper 1 Summer 2024 examination
#this code should be used in conjunction with the Preliminary Material
#written by the AQA Programmer Team
#developed in the Python 3.9.4 programming environment

import random
import os
# import os for file handling stuff???????

def Main():
    Again = "y"
    Score = 0
    while Again == "y":
        Filename = input("Press Enter to start a standard puzzle or enter name of file to load: ")
        if len(Filename) > 0:
            MyPuzzle = Puzzle(Filename + ".txt") # passed to load file, don't have to enter extension
        else:
            MyPuzzle = Puzzle(8, int(8 * 8 * 0.6))
            # passing the grid size and number of goes left (38.4 rounded to 38)
        Score = MyPuzzle.AttemptPuzzle()
        print("Puzzle finished. Your score was: " + str(Score))
        Again = input("Do another puzzle? ").lower()

class Puzzle():
    def __init__(self, *args):
        if len(args) == 1:
            self.__Score = 0
            self.__SymbolsLeft = 0
            self.__GridSize = 0
            self.__Grid = []
            self.__AllowedPatterns = []
            self.__AllowedSymbols = []
            print(args[0])
            self.__LoadPuzzle(args[0])
        else:
            self.__Score = 0
            self.__SymbolsLeft = args[1]
            # number of goes left
            self.__GridSize = args[0]
            self.__Grid = []
            # 10% chance of being a blocked cell
            for Count in range(1, self.__GridSize * self.__GridSize + 1):
                if random.randrange(1, 101) < 90:
                    C = Cell()
                else:
                    C = BlockedCell()
                self.__Grid.append(C)
            self.__AllowedPatterns = []
            self.__AllowedSymbols = []
            QPattern = Pattern("Q", "QQ**Q**QQ")
            self.__AllowedPatterns.append(QPattern)
            self.__AllowedSymbols.append("Q")
            XPattern = Pattern("X", "X*X*X*X*X")
            self.__AllowedPatterns.append(XPattern)
            self.__AllowedSymbols.append("X")
            TPattern = Pattern("T", "TTT**T**T")
            self.__AllowedPatterns.append(TPattern)
            self.__AllowedSymbols.append("T")

    def __LoadPuzzle(self, Filename):
        try:
            with open(Filename) as f:
                NoOfSymbols = int(f.readline().rstrip()) # file has number of different symbols within file, used to load
                # rstrip function gets rid of the line after reading
                # next lines in txt file are the allowed symbols wihtin the file
                for Count in range (1, NoOfSymbols + 1):
                    self.__AllowedSymbols.append(f.readline().rstrip())
                NoOfPatterns = int(f.readline().rstrip())
                # have the number of patterns within the file
                # adds patterns to allowed patterns from file, splits into symbol and symbol pattern
                for Count in range(1, NoOfPatterns + 1):
                    Items = f.readline().rstrip().split(",")
                    P = Pattern(Items[0], Items[1])
                    self.__AllowedPatterns.append(P)
                
                # loads gridsize from file
                self.__GridSize = int(f.readline().rstrip())

                # one line is one cell
                # goes through the text file line by line
                # where each line represents a cell
                # converts each line to a cell in the grid
                # also loads the not allowed symbols if pattern has already been made in a 3x3 grid
                for Count in range (1, self.__GridSize * self.__GridSize + 1):
                    Items = f.readline().rstrip().split(",")
                    if Items[0] == "@":
                        C = BlockedCell()
                        self.__Grid.append(C)
                    else:
                        C = Cell()
                        C.ChangeSymbolInCell(Items[0])
                        # if there is more than one not allowed symbol in the text file
                        # handles adding multiple not allowed smybols to the text file
                        for CurrentSymbol in range(1, len(Items)):
                            C.AddToNotAllowedSymbols(Items[CurrentSymbol])
                        self.__Grid.append(C)
                # reads scoere from file
                self.__Score = int(f.readline().rstrip())
                # reads number of turns left in the file
                self.__SymbolsLeft = int(f.readline().rstrip())
        except FileNotFoundError:
            print("Puzzle not loaded")

    def AttemptPuzzle(self):
        Finished = False
        # loop until puzzle is finished
        while not Finished:
            self.DisplayPuzzle()
            print("Current score: " + str(self.__Score))
            Row = -1
            Valid = False

            # pieces of code to get valid row and column
            # currently can enter indexes outside of the range of the grid
            # entering 9,9 wraps around to top left (8, 1)
            # row 6, column 13 -> row 5, column 5

            # wraps around to row as well in modulus e.g. 13 places in row 5
            # 13 % 8 == 5
            # only wraps around for row, not column (except for value 9 for column)
            while not Valid:
                try:
                    Row = int(input("Enter row number: "))
                    Valid = True
                except:
                    pass
            Column = -1
            Valid = False
            while not Valid:
                try:
                    Column = int(input("Enter column number: "))
                    Valid = True
                except:
                    pass
            
            # handles getting inputs from user, outputting choice
            Symbol = self.__GetSymbolFromUser()
            self.__SymbolsLeft -= 1
            print(Row, Column)

            # checks to see if the symbol is allowed to be added to the class
            # calls method in cell class 
            # checks to see if score needs to be added to class as well
            CurrentCell = self.__GetCell(Row, Column)
            if CurrentCell.CheckSymbolAllowed(Symbol):
                CurrentCell.ChangeSymbolInCell(Symbol)
                AmountToAddToScore = self.CheckforMatchWithPattern(Row, Column)
                if AmountToAddToScore > 0:
                    self.__Score += AmountToAddToScore
            if self.__SymbolsLeft == 0:
                Finished = True
        print()
        self.DisplayPuzzle()
        print()
        return self.__Score

    def __GetCell(self, Row, Column):
        # imagine putting the grid into a straight line
        # then indexing into the list
        Index = (self.__GridSize - Row) * self.__GridSize + Column - 1
        if Index >= 0:
            return self.__Grid[Index]
        else:
            raise IndexError()

    def CheckforMatchWithPattern(self, Row, Column):

        # iterates through possible 3x3 grids near the selected grid
        # from the grid that the user adds a symbol 
        # rows are in decreasing order from top to bottom,
        # starts from top left, moves across columns
        # indexes down a row, continues moving through the columns
        # uses try and except if out of bounds
        for StartRow in range(Row + 2, Row - 1, -1):
            for StartColumn in range(Column - 2, Column + 1):
                print(f"indexing into {StartRow, StartColumn}")
                try:

                    # gets the pattern string for the 3x3 grid that indexing is start from
                    # looks at the grid from the cell the user adds the symbol to
                    # looks at 3x3 grid with center being the cell, starting from top left
                    # going clockwise round to the center of the grid
                    # like snail sort
                    PatternString = ""
                    PatternString += self.__GetCell(StartRow, StartColumn).GetSymbol()
                    PatternString += self.__GetCell(StartRow, StartColumn + 1).GetSymbol()
                    PatternString += self.__GetCell(StartRow, StartColumn + 2).GetSymbol()
                    PatternString += self.__GetCell(StartRow - 1, StartColumn + 2).GetSymbol()
                    PatternString += self.__GetCell(StartRow - 2, StartColumn + 2).GetSymbol()
                    PatternString += self.__GetCell(StartRow - 2, StartColumn + 1).GetSymbol()
                    PatternString += self.__GetCell(StartRow - 2, StartColumn).GetSymbol()
                    PatternString += self.__GetCell(StartRow - 1, StartColumn).GetSymbol()
                    PatternString += self.__GetCell(StartRow - 1, StartColumn + 1).GetSymbol()

                    # looks for matches with all the allowed patterns
                    # private attribute for string representation of pattern string
                    # so uses getter method GetPatternSequence() 
                    for P in self.__AllowedPatterns:
                        print(P.GetPatternSequence())
                        CurrentSymbol = self.__GetCell(Row, Column).GetSymbol()
                        if P.MatchesPattern(PatternString, CurrentSymbol):

                            # if the pattern string matches one of the allowed patterns that earn points
                            # set all the cells in the 3x3 grid with the center being the place the center cell of the matched pattern
                            # add the current symbol that made the pattern to the not allowed symbols for all the cells in the 3x3 grid
                            self.__GetCell(StartRow, StartColumn).AddToNotAllowedSymbols(CurrentSymbol)
                            self.__GetCell(StartRow, StartColumn + 1).AddToNotAllowedSymbols(CurrentSymbol)
                            self.__GetCell(StartRow, StartColumn + 2).AddToNotAllowedSymbols(CurrentSymbol)
                            self.__GetCell(StartRow - 1, StartColumn + 2).AddToNotAllowedSymbols(CurrentSymbol)
                            self.__GetCell(StartRow - 2, StartColumn + 2).AddToNotAllowedSymbols(CurrentSymbol)
                            self.__GetCell(StartRow - 2, StartColumn + 1).AddToNotAllowedSymbols(CurrentSymbol)
                            self.__GetCell(StartRow - 2, StartColumn).AddToNotAllowedSymbols(CurrentSymbol)
                            self.__GetCell(StartRow - 1, StartColumn).AddToNotAllowedSymbols(CurrentSymbol)
                            self.__GetCell(StartRow - 1, StartColumn + 1).AddToNotAllowedSymbols(CurrentSymbol)
                            return 10
                        
                        # false positive matches can occur as the grid is displayed as a one-dimensional list
                        # can miagine having a q on the right hand side
                        # with its tail sticking out to the right below
                        # if you placed a q symbol on the next row down it would wrap round and be equivlant to the tail of the q

                except:
                    pass
        return 0

    # simple block of code to get input for symbol from user
    def __GetSymbolFromUser(self):
        Symbol = ""
        while not Symbol in self.__AllowedSymbols:
            Symbol = input("Enter symbol: ")
        return Symbol
    
    # prints a horizontal line
    # used for the top and bottom of the grid
    def __CreateHorizontalLine(self):
        Line = "  "
        for Count in range(1, self.__GridSize * 2 + 2):
            Line = Line + "-"
        return Line


    def DisplayPuzzle(self):
        print()
        
        # prints the header (column indexes and line)
        # if statement to check size of the grid
        # if grid size larger than 10 then doesn't print the column indexes
        if self.__GridSize < 10:
            print("  ", end='')
            for Count in range(1, self.__GridSize + 1):
                print(" " + str(Count), end='')
        print()
        print(self.__CreateHorizontalLine())
        for Count in range(0, len(self.__Grid)):
            if Count % self.__GridSize == 0 and self.__GridSize < 10:
                print(str(self.__GridSize - ((Count + 1) // self.__GridSize)) + " ", end='')
            print("|" + self.__Grid[Count].GetSymbol(), end='')
            if (Count + 1) % self.__GridSize == 0:
                print("|")
                print(self.__CreateHorizontalLine())

class Pattern():
    def __init__(self, SymbolToUse, PatternString):
        self.__Symbol = SymbolToUse
        self.__PatternSequence = PatternString

    def MatchesPattern(self, PatternString, SymbolPlaced):
        if SymbolPlaced != self.__Symbol:
            return False
        for Count in range(0, len(self.__PatternSequence)):
            try:
                if self.__PatternSequence[Count] == self.__Symbol and PatternString[Count] != self.__Symbol:
                    return False
            except Exception as ex:
                print(f"EXCEPTION in MatchesPattern: {ex}")
        return True

    def GetPatternSequence(self):
      return self.__PatternSequence

class Cell():
    def __init__(self):
        self._Symbol = ""
        self.__SymbolsNotAllowed = []

    def GetSymbol(self):
        if self.IsEmpty():
          return "-"
        else:
          return self._Symbol
    
    def IsEmpty(self):
        if len(self._Symbol) == 0:
            return True
        else:
            return False

    def ChangeSymbolInCell(self, NewSymbol):
        self._Symbol = NewSymbol

    def CheckSymbolAllowed(self, SymbolToCheck):
        for Item in self.__SymbolsNotAllowed:
            if Item == SymbolToCheck:
                return False
        return True

    def AddToNotAllowedSymbols(self, SymbolToAdd):
        self.__SymbolsNotAllowed.append(SymbolToAdd)

    def UpdateCell(self):
        pass

class BlockedCell(Cell):
    def __init__(self):
        super(BlockedCell, self).__init__()
        self._Symbol = "@"

    def CheckSymbolAllowed(self, SymbolToCheck):
        return False

if __name__ == "__main__":
    Main()
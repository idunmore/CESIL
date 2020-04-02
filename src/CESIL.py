import enum

def cesil():
    print("CESIL (Computer Education in Schools Instruction Language")

    interpreter = CESIL()
    #interpreter.tokenize("**")
    #print( interpreter.is_legal_identifier('A123'))
    #print( interpreter.is_instruction('BOO') )

    #print( "Comments" )
    #print( interpreter.is_comment( '* Hello World'))
    #print( interpreter.is_comment( '** Hello World'))
    #print( interpreter.is_comment( '*() Hello World'))
    #print( interpreter.is_comment( '() Hello World'))
    #print( interpreter.is_comment( 'LABEL LOOP LABEL Hello World'))
  
    interpreter.load_file( r'./examples/Syntax_Test.ces')
    pass

class ElementType(enum.Enum):
    Comment = 0
    Label = 1
    Instruction = 2
    Operand = 3
    InlineComment = 4

class Element:

    def __init__(self, value, type ):
        self.value = value
        self.type = type

class Line:

    def __init__(self, element1, element2, element3, element4):  
        self.element1 = element1
        self.element2 = element2
        self.element3 = element3
        self.element4 = element4

    def getLine():
        if element1.type == ElementType.Comment: return element1.value
        line = ''


class OpType(enum.Enum):
    NoArg = 0
    Label = 1
    Literal = 2
    Var = 3
    LiteralOrVar = 4
    
class CESIL:

    # Class Data
    instructions =  { 
        'IN': OpType.NoArg, 'OUT': OpType.NoArg, 'LINE': OpType.NoArg, 'HALT': OpType.NoArg,
        'LOAD': OpType.LiteralOrVar, 'STORE': OpType.LiteralOrVar, 'ADD': OpType.LiteralOrVar,
        'SUBTRACT': OpType.LiteralOrVar, 'MULTIPLY': OpType.LiteralOrVar, "DIVIDE": OpType.LiteralOrVar,
        'PRINT': OpType.Literal, 'JUMP': OpType.Label, 'JIZERO': OpType.Label, 'JINEG': OpType.Label
    }
    
    comment_prefix = ['*', '(', '**', '*C']

    # Methods
    def __init__(self):
        self.accumulator = 0
        self.program_lines = []

    def load_file(self, filename):
        lineNumber = 1
        with open( filename, 'r' ) as reader:
            for line in reader:
                print( '#{0:>4} {1:<8} (C={2:<})'.format( lineNumber, line[:-1], str(CESIL.is_comment(line)) ) )
                lineNumber = lineNumber + 1


    def tokenize( self, line ):
        parts = line.split()
        print(line)
        print(parts)
        if len(parts) > 0:
            # Valid Instruction?
            if parts[0] in self.instructions:
                # Yes
                #if parts[0] ==  print("Comment!")
                pass
            else:
                pass

    @staticmethod
    def is_comment(line):
        # Is the line a comment?
        return len(line) > 0 and line[0] in CESIL.comment_prefix
    
    @staticmethod
    def is_legal_identifier(identifier):
        # Identifiers must be between 1 and 6 characters, START with an alpha, contain only alpha-numerics and NOT be a reserved word/instruction.
        return not CESIL.is_instruction(identifier) and (len(identifier) > 0 and len(identifier) <= 6) and (identifier[0].isalpha() and (len(identifier) == 1 or identifier[1:].isalnum()))

    @staticmethod
    def is_instruction(instruction):
        return instruction in CESIL.instructions

# Run!
if __name__ == '__main__':
    cesil() 
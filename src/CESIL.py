import enum

def cesil():
    print("CESIL (Computer Education in Schools Instruction Language")

    interpreter = CESIL()
    #interpreter.tokenize("**")
    print( interpreter.is_legal_identifier('A12345'))
    print( interpreter.is_instruction('BOO') )
    
    
    pass

class OperandType(enum.Enum):
    Ignore = 0
    NoArgument = 1
    Label = 2
    Literal = 3
    Variable = 4
    LiteralOrVariable = 5
    
class CESIL:

    # Class Data
    instructions =  {
        '**': OperandType.Ignore, '*C': OperandType.Ignore, '*': OperandType.Ignore, '(': OperandType.Ignore,
        'IN': OperandType.NoArgument, 'OUT': OperandType.NoArgument, 'LINE': OperandType.NoArgument, 'HALT': OperandType.NoArgument,
        'LOAD': OperandType.LiteralOrVariable, 'STORE': OperandType.LiteralOrVariable, 'PRINT': OperandType.Literal,
        'ADD': OperandType.LiteralOrVariable, 'SUBTRACT': OperandType.LiteralOrVariable, 'MULTIPLY': OperandType.LiteralOrVariable, "DIVIDE": OperandType.LiteralOrVariable,
        'JUMP': OperandType.Label, 'JIZERO': OperandType.Label, 'JINEG': OperandType.Label }

    # Methods
    def __init__(self):
        self.accumulator = 0
        self.program_lines = []

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

    def proc_line(line):
        # Is the line a comment?
        if len(line) > 0:
            if line[0] == '*' or line[0] == 'C'

        pass

    @classmethod
    def is_legal_identifier(cls, identifier):
        # Identifiers must be between 1 and 6 characters, start with an alpha and contain only alpha-numerics
        return (len(identifier) > 0 and len(identifier) <= 6) and (identifier[0].isalpha() and (len(identifier) == 1 or identifier[1:].isalnum()))

    @classmethod
    def is_instruction(cls, instruction):
        return instruction in CESIL.instructions
        

            
# Run!
if __name__ == '__main__':
    cesil() 
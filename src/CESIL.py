import enum

def cesil():
    print("CESIL (Computer Education in Schools Instruction Language")

    interpreter = CESIL()
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
    LiteralOrVar = 3
    
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
        self._accumulator = 0
        self._program_lines = []
        self._data_values = []
        self._labels = {}
        self._variables = {}

    def load_file(self, filename):
        isCodeSection = True
        lineNumber = 0
        with open( filename, 'r' ) as reader:
            for line in reader:
                lineNumber = lineNumber + 1
                # Skip blank lines and comments.
                if len(line) == 0 or line == '\n' or CESIL.is_comment(line): continue

                if isCodeSection == True:           
                    # Transition from Code to Data?
                    if CESIL.is_data_start(line):
                        isCodeSection = False
                        continue
                    else:
                        # Process Code Line
                        self.parse_code_line(line)
                    
                else:
                    # We're in the Data Section, so add any data on this line to our data values.                    
                    if line[0] != '*': 
                        for data in line.split(): self._data_values.append(int(data))


    def parse_code_line(self, line):
        # Break up the line, before figuring out what bits are where.
        parts = line.split()
        currentPart = 0
        lastPart = len(parts) -1
        label = None
        instruction = None
        operand = None

        # TODO: For labels, resolve the instruction pointer (need to add an instruction pointer)
        # and us it in place of the 0 (ZERO) we're currently inserting!
        if CESIL.is_legal_identifier(parts[currentPart]):
            # We have a label ...
            label = parts[currentPart]
            if currentPart < lastPart: currentPart = currentPart + 1
            self._labels[label] = 0
        
        if CESIL.is_instruction(parts[currentPart]):
            # We have an instruction
            instruction = parts[currentPart]
            opType = CESIL.instructions[instruction]
            
            # TODO: Streamline so that we abort with errors if we find them as we go,
            # and otherwise only do the operand = potentialOperand assignement ONCE
            # at the end of processing.

            # TODO: 
            # Get Operand if there is one.
            if opType != OpType.NoArg :
                if currentPart < lastPart: currentPart = currentPart + 1
                potentialOperand = parts[currentPart]
                # Validate the potential operand
                if opType == OpType.Label and CESIL.is_legal_identifier(potentialOperand):
                    operand = potentialOperand
                else:
                    # Error
                    pass

                if opType == OpType.LiteralOrVar:
                    if CESIL.is_legal_identifier(potentialOperand):
                        operand = potentialOperand
                        self._variables[operand] = 0
                    elif CESIL.is_legal_integer(potentialOperand):
                        operand = int(potentialOperand)
                    else:   
                        #Error
                        pass

                if opType == OpType.Literal:
                    operand = potentialOperand

        print('Label: {0} - Instruction: {1} - Operand: {2}'.format(label, instruction, operand))



    def what_is_part(part):
        if CESIL.is_legal_identifier(): return 

    @staticmethod
    def is_legal_integer(value):
        try:
            num = int(value)
            return (num >= -8388608 and num <= 8388607)
        except:
            return False

    @staticmethod
    def is_data_start(line):
        # Data section starts with a %
        return line[0] == '%'

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
import enum

def cesil():
   
    interpreter = CESIL()
    #interpreter.load_file( r'./examples/Syntax_Test.ces')
    interpreter.load_file( r'./examples/Wikipedia.ces')
    #interpreter.load_file( r'./examples/99Beers.ces')

    interpreter.run()

class OpType(enum.Enum):
    NoArg = 0
    Label = 1
    Literal = 2
    LiteralOrVar = 3
    Var = 4

class CodeLine():
    def __init__(self, label, instruction, operand):
        self.label = label
        self.instruction = instruction
        self.operand = operand
        self.lineNumber = 0
    
class CESIL:

    # Class Data
    instructions = { 
        'IN': OpType.NoArg, 'OUT': OpType.NoArg, 'LINE': OpType.NoArg, 'HALT': OpType.NoArg,
        'LOAD': OpType.LiteralOrVar, 'STORE': OpType.Var, 'ADD': OpType.LiteralOrVar,
        'SUBTRACT': OpType.LiteralOrVar, 'MULTIPLY': OpType.LiteralOrVar, "DIVIDE": OpType.LiteralOrVar,
        'PRINT': OpType.Literal, 'JUMP': OpType.Label, 'JIZERO': OpType.Label, 'JINEG': OpType.Label
    }
    
    comment_prefix = ['*', '(', '**', '*C']

    # Methods
    def __init__(self):
        self._program_lines = []
        self._data_values = []
        self._labels = {}
        self._variables = {}

    def load_file(self, filename):
        isCodeSection = True
        lineNumber = 0
        instruction_index = 0
        with open(filename, 'r') as reader:
            for line in reader:
                lineNumber = lineNumber + 1
                # Skip blank lines and comments.
                if len(line) == 0 or line == '\n' or CESIL.is_comment(line): continue

                if isCodeSection == True:           
                    # Transition from Code to Data?
                    if CESIL.is_data_start(line):
                        isCodeSection = False
                    else:
                        # Process Code Line
                        codeLine = self.parse_code_line(line)
                        if codeLine.label != None: self._labels[codeLine.label] = instruction_index
                        if codeLine.instruction != None:
                            codeLine.lineNumber = lineNumber
                            self._program_lines.append(codeLine)
                        instruction_index = instruction_index + 1                    
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
            # and otherwise only do the operand = potential Operand assignement ONCE
            # at the end of processing.

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

                if opType == OpType.LiteralOrVar or opType == OpType.Var:
                    if CESIL.is_legal_identifier(potentialOperand):
                        operand = potentialOperand
                        self._variables[operand] = 0
                    elif CESIL.is_legal_integer(potentialOperand):
                        operand = int(potentialOperand)
                    else:   
                        #Error
                        pass
                
                # Only applies to PRINT, which needs special handling.
                if opType == OpType.Literal:
                    # Put SPLIT parts back together for PRINT "" strings                    
                    while currentPart < lastPart:
                        currentPart = currentPart + 1
                        potentialOperand = potentialOperand + ' ' + parts[currentPart]

                    # Strip Quotes and any trailing comment.
                    operand = potentialOperand[potentialOperand.find('"')+1:potentialOperand.rfind('"')]

        return CodeLine(label, instruction, operand)

    def run(self):
        accumulator = 0
        instructionPtr = 0
        dataPtr = 0
        while instructionPtr < len(self._program_lines):
            line = self._program_lines[instructionPtr]
            
            # Execute the instruction, based on what it is.
            if line.instruction == 'HALT': break

            if line.instruction == 'IN':
                accumulator = int(self._data_values[dataPtr])
                dataPtr = dataPtr + 1
            elif line.instruction == 'OUT':
                print(accumulator, end='')
            elif line.instruction == 'LOAD':
                accumulator = self._get_real_value(line.operand)
            elif line.instruction == 'STORE':
                if CESIL.is_legal_identifier(line.operand):
                    self._variables[line.operand] = accumulator                    
            elif line.instruction == 'LINE':
                print('')
            elif line.instruction == 'PRINT':
                print(line.operand, end='')
            elif line.instruction == 'ADD':
                accumulator = accumulator + self._get_real_value(line.operand)
            elif line.instruction == 'SUBTRACT': 
                accumulator = accumulator - self._get_real_value(line.operand)
            elif line.instruction == 'MULTIPLY': 
                accumulator = accumulator * self._get_real_value(line.operand)
            elif line.instruction == 'DIVIDE': 
                accumulator = accumulator / self._get_real_value(line.operand)
            elif line.instruction == 'JUMP':
                instructionPtr = self._labels[line.operand]
                continue
            elif line.instruction == 'JIZERO':
                if accumulator == 0:
                    instructionPtr = self._labels[line.operand]
                    continue
            elif line.instruction == 'JINEG':
                if accumulator < 0:
                    instructionPtr = self._labels[line.operand]
                    continue

            # If nothing else has changed the execution path, move to the next instruction
            instructionPtr = instructionPtr + 1

    def _get_real_value(self, operand):
        return int(self._variables[operand] if CESIL.is_legal_identifier(operand) else operand)
   
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
        try:
            # Identifiers must be between 1 and 6 characters, START with an alpha, contain only alpha-numerics and NOT be a reserved word/instruction.
            return not CESIL.is_instruction(identifier) and (len(identifier) > 0 and len(identifier) <= 6) and (identifier[0].isalpha() and (len(identifier) == 1 or identifier[1:].isalnum()))
        except:
            return False

    @staticmethod
    def is_instruction(instruction):
        return instruction in CESIL.instructions

# Run!
if __name__ == '__main__':
    cesil() 
# CESIL Plus - Computer Education in Schools Instruction Lanaguage
#              Interpreter w/ optional Extensions
#
# Author : Ian Michael Dunmore
# Date   : 05/02/2020
#
# License: https://github.com/idunmore/CESIL/blob/master/LICENSE

import enum
import re
import click

# Classes

# Operand Types - Value types of Operand for an Instruction
class OpType(enum.Enum):
    NONE = 0
    LABEL = 1
    LITERAL = 2
    LITERAL_VAR = 3
    VAR = 4
    
# Code Line - Represents the processable elements of Line of Code
class CodeLine():
    def __init__(self, label, instruction, operand):
        self.label = label
        self.instruction = instruction
        self.operand = operand
        self.line_number = 0

# Program - Represents the overall program, variable, labels and data
class Program():
    def __init__(self):
        self.program_lines = []
        self.data_values = []
        self.labels = {}
        self.variables = {}

# Constants

# CESIL identifiers/labels consist of up to 6 uppercase alphanumeric
# characters, starting with a letter (e.g. A12345)
IDENTIFIER_PATTERN = re.compile('^[A-Z][A-Z0-9]{0,5}')

# CESIL integers are signed 24-bit values from -8388608 to +8388607
VALUE_MAX = 8388607
VALUE_MIN = -8388608

# CESIL comments begin with a *, but on punched-cards from coding sheets
# can also start with (, ** and *C
COMMENT_PREFIX = ['*', '(', '**', '*C']

# The data section in a CESIL program starts with a % on a new line
START_DATA_SECTION = '%'

# CESIL Instructions (default CESIL language, without extensions)
INSTRUCTIONS = {
    'IN': OpType.NONE, 'OUT': OpType.NONE, 'LINE': OpType.NONE,
    'HALT': OpType.NONE,
    'LOAD': OpType.LITERAL_VAR, 'STORE': OpType.LITERAL_VAR,
    'ADD': OpType.LITERAL_VAR, 'SUBTRACT': OpType.LITERAL_VAR,
    'MULTIPLY': OpType.LITERAL_VAR, 'DIVIDE': OpType.LITERAL_VAR,
    'PRINT': OpType.LITERAL,
    'JUMP': OpType.LABEL, 'JIZERO': OpType.LABEL, 'JINEG': OpType.LABEL
}

@click.command()
@click.option('-s', '--source',
    type=click.Choice(['t', 'text', 'c', 'card'], case_sensitive=False),
    default='text', show_default=True, help='Text or punched Card input.')
@click.option('-d', '--debug',
    type=click.Choice(['0', '1', '2'], case_sensitive=False),
        default='0', show_default=True, help='Debug mode/verbosity level.')
@click.option('-p', '--plus', is_flag=True, default=False,
    help='Enables "plus" mode language extensions.')
@click.version_option('0.1.0')
@click.argument('source_file', type=click.Path(exists=True))
def cesilplus(source, debug, plus, source_file):
    """CESILPlus - CESIL Interpreter (w/ optional language extentions).
    
    \b
      CESIL: Computer Eduction in Schools Instruction Language

      "Plus" language extensions add a STACK to the language, enabled
    with the -p | --plus options.  Extensions are DISABLED by default.

      Extension instructions: PUSH, POP

    \b
        PUSH       - Pushes ACCUMULATOR value on to STACK
        POP        - Pops top value from STACK into the ACCUMULATOR             
    """
    
    # Add "Plus" extension instructions, if "Plus" mode is selected
    if plus:
        INSTRUCTIONS['POP'] = OpType.NONE
        INSTRUCTIONS['PUSH'] = OpType.NONE

    # Parsed program, variable and data storage - for execution
    program = load_program(source_file, source)    
    
    # Execute program ...
    run(program)

def load_program(filename, source_format):
    # Determine if we're parsing text file format or punch card
    is_text = True if source_format[0].upper() == 'T' else False

    program = Program()
    isCodeSection = True
    lineNumber = 0
    instruction_index = 0

    with open(filename, 'r') as reader:
        for line in reader:
            lineNumber = lineNumber + 1
            # Skip blank lines and comments.
            if len(line) == 0 or line == '\n' or is_comment(line): continue

            if isCodeSection == True:           
                # Transition from Code to Data?
                if is_data_start(line):
                    isCodeSection = False
                else:
                    # Process Code Line
                    codeLine = parse_code_line(program, line, is_text)
                    
                    # Add an instruction pointer for a label
                    if codeLine.label != None: 
                        program.labels[codeLine.label] = instruction_index

                    # Add a code line to the program if there's an instruction
                    if codeLine.instruction != None:
                        codeLine.lineNumber = lineNumber
                        program.program_lines.append(codeLine)

                    instruction_index = instruction_index + 1                    
            else:
                # We're in the Data Section, so add any data on this line to
                # our data values.                    
                if line[0] != '*': 
                    for data in line.split():
                        program.data_values.append(int(data))

    return program

# Parses a line of code using TEXT FILE formatting/layout rules
def parse_code_line(program, line, is_text):

    parts = None

    # Break up the line, before figuring out what bits are where.
    if is_text:
        parts = line.split()
    else:
        parts = split_punch_card_line(line)

    currentPart = 0
    lastPart = len(parts) -1
    label = None
    instruction = None
    operand = None

    if is_legal_identifier(parts[currentPart]):
        # We have a label ...
        label = parts[currentPart]
        if currentPart < lastPart: currentPart = currentPart + 1
        program.labels[label] = 0
    
    if is_instruction(parts[currentPart]):
        # We have an instruction
        instruction = parts[currentPart]
        opType = INSTRUCTIONS[instruction]
                   
        # TODO: Streamline so that we abort with errors if we find them as we
        # go, and otherwise only do the operand = potential Operand
        # assignement ONCE at the end of processing.

        # Get Operand if there is one.
        if opType != OpType.NONE:
            if currentPart < lastPart: currentPart = currentPart + 1
            potentialOperand = parts[currentPart]
            # Validate the potential operand
            if opType == OpType.LABEL and is_legal_identifier(potentialOperand):
                operand = potentialOperand
            else:
                # Error
                pass

            if opType == OpType.LITERAL_VAR or opType == OpType.VAR:
                if is_legal_identifier(potentialOperand):
                    operand = potentialOperand
                    program.variables[operand] = 0
                elif is_legal_integer(potentialOperand):
                    operand = int(potentialOperand)
                else:   
                    #Error
                    pass
            
            # Only applies to PRINT, which needs special handling.
            if opType == OpType.LITERAL:
                # Put SPLIT parts back together for PRINT "" strings                    
                while currentPart < lastPart:
                    currentPart = currentPart + 1
                    potentialOperand = potentialOperand + ' ' + parts[currentPart]

                # Strip Quotes and any trailing comment.
                operand = potentialOperand[potentialOperand.find('"')+1:potentialOperand.rfind('"')]

    return CodeLine(label, instruction, operand)

def split_punch_card_line(line):
    parts = []
    length = len(line)

    if length <= 8:
        # Only a label on this line:
        parts.append(line.strip())
    elif length <= 16:
        # Instruction, with or without label
        parts.append(line[0:8].strip())
        parts.append(line[8:16].strip())
    else:
        # Instruction and operand, with or without label
        parts.append(line[0:8].strip())
        parts.append(line[8:16].strip())

        # If the operand is a string, make sure that's all we extract
        operand = line[16:].strip()
        if operand[0] == '"':
            # This is a string, so find the next " character.
            end_quote = operand.find('"', 1)
            if end_quote > 0:
                operand = operand[0:end_quote]
            else:
                # TODO: Unterminated string is an error!  How to handle?
                pass

        parts.append(operand)
        
    return parts


def run(program):
    accumulator = 0
    stack = []
    instructionPtr = 0
    dataPtr = 0
    while instructionPtr < len(program.program_lines):
        line = program.program_lines[instructionPtr]
        variables = program.variables

        # Execute the instruction, based on what it is.
        if line.instruction == 'HALT': break

        if line.instruction == 'IN':
            accumulator = int(program.data_values[dataPtr])
            dataPtr = dataPtr + 1
        elif line.instruction == 'OUT':
            print(accumulator, end='')
        elif line.instruction == 'LOAD':
            accumulator = get_real_value(variables, line.operand)
        elif line.instruction == 'STORE':
            if is_legal_identifier(line.operand):
                variables[line.operand] = accumulator                    
        elif line.instruction == 'LINE':
            print('')
        elif line.instruction == 'PRINT':
            print(line.operand, end='')
        elif line.instruction == 'ADD':
            accumulator = accumulator + get_real_value(variables, line.operand)
        elif line.instruction == 'SUBTRACT': 
            accumulator = accumulator - get_real_value(variables, line.operand)
        elif line.instruction == 'MULTIPLY': 
            accumulator = accumulator * get_real_value(variables, line.operand)
        elif line.instruction == 'DIVIDE': 
            accumulator = accumulator / get_real_value(variables, line.operand)
        elif line.instruction == 'JUMP':
            instructionPtr = program.labels[line.operand]
            continue
        elif line.instruction == 'JIZERO':
            if accumulator == 0:
                instructionPtr = program.labels[line.operand]
                continue
        elif line.instruction == 'JINEG':
            if accumulator < 0:
                instructionPtr = program.labels[line.operand]
                continue       
        elif line.instruction == 'POP':
            accumulator = stack.pop
            continue
        elif line.instruction == 'PUSH':
            stack.append(accumulator)
            continue

        # If nothing else has changed the execution path, move to the next instruction
        instructionPtr = instructionPtr + 1

def get_real_value(variables, operand):
    return int(variables[operand] if is_legal_identifier(operand) else operand)

def is_comment(line):
    return len(line) > 0 and line[0] in COMMENT_PREFIX

def is_legal_identifier(identifier):
    if is_instruction(identifier):
        # Instructions are RESERVED words and NOT legal identifiers!
        return False
    else:
        return re.fullmatch(IDENTIFIER_PATTERN, str(identifier)) is not None

def is_legal_integer(value):
    try:
        num = int(value)
        return (num >= VALUE_MIN and num <= VALUE_MAX)
    except:
        return False

def is_instruction(instruction):
    return instruction in INSTRUCTIONS

def is_data_start(line):
    return len(line) > 0 and line[0] == START_DATA_SECTION

# Run!
if __name__ == '__main__':
    cesilplus() 
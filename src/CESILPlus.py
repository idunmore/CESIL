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

      "Plus" language extensions add a STACK and SUBROUTINE support to
    the language, enabled with the -p | --plus options.  Extensions are
    DISABLED by default.

      "Plus" Mode - Extension instructions:

    \b
        PUSH          - PUSHes the ACCUMULATOR value on to STACK
        POP           - POPs top value from STACK into the ACCUMULATOR
        
        JUMPSR  label - Jumps to SUBROUTINE @ label
        JSIZERO label - Jumps to SUBROUTINE @ label if ACCUMULATOR = 0
        JSINEG  label - Jumps to SUBROUTINE @ label if ACCUMULATOR < 0
        RETURN        - Returns from SUBROUTINE and continues execution
    """
    
    # Add "Plus" extension instructions, if "Plus" mode is selected
    if plus:
        # Stack Instructions
        INSTRUCTIONS['POP'] = OpType.NONE
        INSTRUCTIONS['PUSH'] = OpType.NONE
        # Subroutine Instructions
        INSTRUCTIONS['RETURN'] = OpType.NONE
        INSTRUCTIONS['JSINEG'] = OpType.LABEL
        INSTRUCTIONS['JSIZERO'] = OpType.LABEL
        INSTRUCTIONS['JUMPSR'] = OpType.LABEL

    # Parsed program, variable and data storage - for execution ...
    program = load_program(source_file, source)    
    # ... and excute it ...
    run(program)

# Loads program from a file, observing TEXT or PUNCH CARD formatting
def load_program(filename, source_format):
    # Determine if we're parsing text file format or punch card
    is_text = True if source_format[0].upper() == 'T' else False

    program = Program()
    isCodeSection = True
    lineNumber = 0
    instruction_index = 0

    with open(filename, 'r') as reader:
        for line in reader:
            lineNumber += 1
            # Skip blank lines and comments.
            if len(line.strip()) == 0 or line == '\n' or is_comment(line):
                continue

            if isCodeSection == True:           
                # Transition from Code to Data?
                if is_data_start(line):
                    isCodeSection = False
                else:
                    # Process Code Line
                    codeLine = parse_code_line(line, is_text)
                    
                    # Add the label, if present, with its instruction pointer
                    if codeLine.label != None: 
                        program.labels[codeLine.label] = instruction_index

                    # Add the variable, if present, initialized to zero
                    if is_legal_identifier(codeLine.operand):
                        program.variables[codeLine.operand] = 0

                    # Add a code line to the program if there's an instruction
                    if codeLine.instruction != None:
                        codeLine.lineNumber = lineNumber
                        program.program_lines.append(codeLine)

                    instruction_index += 1                    
            else:
                # We're in the Data Section, so add any data on this line to
                # our data values.                    
                if line[0] != '*': 
                    for data in line.split():
                        program.data_values.append(int(data))

    return program

# Parses a line of code, accounting for TEXT or PUNCH CARD formatting
def parse_code_line(line, is_text):

    # Break up the line, before figuring out what bits are where,
    # using different splitting approaches for text vs. punch card.
    parts = None
    parts = line.split() if is_text else split_punch_card_line(line)
    
    currentPart = 0
    lastPart = len(parts) -1
    label = None
    instruction = None
    operand = None

    if is_legal_identifier(parts[currentPart]):
        # We have a label ...
        label = parts[currentPart]
        if currentPart < lastPart: currentPart +=  1
           
    if is_instruction(parts[currentPart]):
        # We have an instruction
        instruction = parts[currentPart]
        opType = INSTRUCTIONS[instruction]
                   
        # TODO: Streamline so that we abort with errors if we find them as we
        # go, and otherwise only do the operand = potential Operand
        # assignement ONCE at the end of processing.

        # Get the Operand if there is one.
        if opType != OpType.NONE:
            if currentPart < lastPart: currentPart += 1
            potentialOperand = parts[currentPart]
            # Validate the potential operand
            if ( opType == OpType.LABEL
                 and is_legal_identifier(potentialOperand) ):
                    operand = potentialOperand
            else:
                # Error
                pass

            if opType == OpType.LITERAL_VAR or opType == OpType.VAR:
                if is_legal_identifier(potentialOperand):
                    operand = potentialOperand                    
                elif is_legal_integer(potentialOperand):
                    operand = int(potentialOperand)
                else:   
                    # Error
                    pass
            
            # Only applies to PRINT, which needs special handling.
            if opType == OpType.LITERAL:
                # Put SPLIT parts back together for PRINT "" strings                    
                while currentPart < lastPart:
                    currentPart += 1
                    potentialOperand += ' ' + parts[currentPart]

                # Strip Quotes and any trailing comment.
                operand = potentialOperand[potentialOperand.find('"')+1:
                            potentialOperand.rfind('"')]

    return CodeLine(label, instruction, operand)

# Splits up source-code lines based on PUNCH CARD column settings.
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

# Executes the specified, parsed, CESIL program.
def run(program):
    # "Pure" CESIL execution state
    accumulator = 0
    instruction_ptr = 0
    data_ptr = 0

    # "Plus" execution state
    stack = []
    call_stack = []

    # Shorter references for frequently accessed program elements
    variables = program.variables
    labels = program.labels

    # Iterate the "program", 
    while instruction_ptr < len(program.program_lines):
        line = program.program_lines[instruction_ptr]
        
        # Execute the instruction, based on what it is.
        if line.instruction == 'HALT': break

        if line.instruction == 'IN':
            accumulator = int(program.data_values[data_ptr])
            data_ptr += 1
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
            accumulator += get_real_value(variables, line.operand)
        elif line.instruction == 'SUBTRACT': 
            accumulator -= get_real_value(variables, line.operand)
        elif line.instruction == 'MULTIPLY': 
            accumulator *= get_real_value(variables, line.operand)
        elif line.instruction == 'DIVIDE': 
            accumulator /= get_real_value(variables, line.operand)
        elif line.instruction == 'JUMP':
            instruction_ptr = labels[line.operand]
            continue
        elif line.instruction == 'JIZERO':
            if accumulator == 0:
                instruction_ptr = labels[line.operand]
                continue
        elif line.instruction == 'JINEG':
            if accumulator < 0:
                instruction_ptr = labels[line.operand]
                continue
        elif line.instruction == 'RETURN':
            instruction_ptr = call_stack.pop()
        elif line.instruction == 'JUMPSR':
            call_stack.append(instruction_ptr)
            instruction_ptr = labels[line.operand]
            continue
        elif line.instruction == 'JSIZERO':
            if accumulator == 0:
                call_stack.append(instruction_ptr)
                instruction_ptr = labels[line.operand]
                continue
        elif line.instruction == 'JSINEG':
            if accumulator < 0:
                call_stack.append(instruction_ptr)
                instruction_ptr = labels[line.operand]
                continue
        elif line.instruction == 'POP':
            accumulator = stack.pop()
        elif line.instruction == 'PUSH':
            stack.append(accumulator)

        # If nothing else has changed the execution path, move to the
        # next instruction
        instruction_ptr += 1

# Resolves Operand value as a LITERAL or from a VARIABLE, and returns it.
def get_real_value(variables, operand):
    return int(variables[operand] if is_legal_identifier(operand) else operand)

# Determines if the line is a comment.
def is_comment(line):
    return len(line) > 0 and line[0] in COMMENT_PREFIX

# Determines if the IDENTIFIER is legal in CESIL
def is_legal_identifier(identifier):
    if is_instruction(identifier):
        # Instructions are RESERVED words and NOT legal identifiers!
        return False
    else:
        return re.fullmatch(IDENTIFIER_PATTERN, str(identifier)) is not None

# Bounds checks a value as a legal INTEGER (24-bit, signed).
def is_legal_integer(value):
    try:
        num = int(value)
        return (num >= VALUE_MIN and num <= VALUE_MAX)
    except:
        return False

# Determine if arugment is a valid CESIL (or CESIL Plus) instruction.
def is_instruction(instruction):
    return instruction in INSTRUCTIONS

# Determine if this line indicates the start of the "Data Section"
def is_data_start(line):
    return len(line) > 0 and line[0] == START_DATA_SECTION

# Run!
if __name__ == '__main__':
    cesilplus() 
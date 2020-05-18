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

# State - Represents the current execution state of the Program
class State():
    def __init__(self):
        # Pure CESIL state
        self.accumulator = 0
        self.instruction_ptr = 0
        self.data_ptr = 0
        # "Plus" execution state
        self.stack = []
        self.call_stack = []

# Exceptions

class CESILException(Exception):
    def __init__(self, line_number, message, code):
        self.line_number = line_number
        self.message = message
        self.code = code
    
    def print(self):
        print('Error {0} at line {1}: {2}',
            self.message, self.line_number, self.code)

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
    type=click.Choice(['0', '1', '2', '3', '4'], case_sensitive=False),
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

    try:
        # Parsed program, variable and data storage - for execution ...
        program = load_program(source_file, source)    
        # ... and excute it ...
        run(program, int(debug))

    except CESILException as err:
        err.print()
    
# Loads program from a file, observing TEXT or PUNCH CARD formatting
def load_program(filename, source_format):
    # Determine if we're parsing text file format or punch card
    is_text = True if source_format[0].upper() == 'T' else False

    program = Program()
    is_code_section = True
    line_number = 0
    instruction_index = 0

    with open(filename, 'r') as reader:
        for line in reader:
            line_number += 1
            # Skip blank lines and comments.
            if len(line.strip()) == 0 or line == '\n' or is_comment(line):
                continue

            if is_code_section == True:           
                # Transition from Code to Data?
                if is_data_start(line):
                    is_code_section = False
                else:
                    # Process Code Line
                    code_line = parse_code_line(line, is_text)
                    
                    # Add the label, if present, with its instruction pointer
                    if code_line.label != None: 
                        program.labels[code_line.label] = instruction_index

                    # Variable? (A legal IDENTIFIER that ISN'T a LABEL)
                    if ( is_legal_identifier(code_line.operand) and                       
                         INSTRUCTIONS[code_line.instruction] ==
                         OpType.LITERAL_VAR):
                            # Add the variable and initialize it                          
                            program.variables[code_line.operand] = 0

                    # Add a code line to the program if there's an instruction
                    if code_line.instruction != None:
                        code_line.line_number = line_number
                        program.program_lines.append(code_line)

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
    
    current_part = 0
    last_part = len(parts) -1
    label = None
    instruction = None
    operand = None

    if is_legal_identifier(parts[current_part]):
        # We have a label ...
        label = parts[current_part]
        if current_part < last_part: current_part +=  1
           
    if is_instruction(parts[current_part]):
        # We have an instruction
        instruction = parts[current_part]
        op_type = INSTRUCTIONS[instruction]
                   
        # TODO: Streamline so that we abort with errors if we find them as we
        # go, and otherwise only do the operand = potential Operand
        # assignement ONCE at the end of processing.

        # Get the Operand if there is one.
        if op_type != OpType.NONE:
            if current_part < last_part: current_part += 1
            potential_operand = parts[current_part]
            # Validate the potential operand
            if ( op_type == OpType.LABEL
                 and is_legal_identifier(potential_operand) ):
                    operand = potential_operand
            else:          
                # Error - Illegal Idenfier?      
                pass

            if op_type == OpType.LITERAL_VAR or op_type == OpType.VAR:
                if is_legal_identifier(potential_operand):
                    operand = potential_operand                    
                elif is_legal_integer(potential_operand):
                    operand = int(potential_operand)
                else:   
                    # Error - Illegal operand
                    pass
            
            # Only applies to PRINT, which needs special handling.
            if op_type == OpType.LITERAL:
                # Put SPLIT parts back together for PRINT "" strings                    
                while current_part < last_part:
                    current_part += 1
                    potential_operand += ' ' + parts[current_part]

                # Strip Quotes and any trailing comment.
                operand = potential_operand[potential_operand.find('"')+1:
                            potential_operand.rfind('"')]

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
def run(program, debug_level):
   # Initialize execution state
    state = State()

    # Shorter references for frequently accessed program elements
    variables = program.variables
    labels = program.labels

    # Iterate the "program", 
    while state.instruction_ptr < len(program.program_lines):
        # Output debug info, if enabled - for line ABOUT to execute!
        if debug_level > 0: debug_out( debug_level, program, state)

        # Get line to execute.
        line = program.program_lines[state.instruction_ptr]
        
        # Execute the instruction, based on what it is.
        if line.instruction == 'HALT': break

        if line.instruction == 'IN':
            state.accumulator = int(program.data_values[data_ptr])
            state.data_ptr += 1
        elif line.instruction == 'OUT':
            print(state.accumulator, end='')
        elif line.instruction == 'LOAD':
            state.accumulator = get_real_value(variables, line.operand)
        elif line.instruction == 'STORE':
            if is_legal_identifier(line.operand):
                variables[line.operand] = state.accumulator                    
        elif line.instruction == 'LINE':
            print('')
        elif line.instruction == 'PRINT':
            print(line.operand, end='')
        elif line.instruction == 'ADD':
            state.accumulator += get_real_value(variables, line.operand)
        elif line.instruction == 'SUBTRACT': 
            state.accumulator -= get_real_value(variables, line.operand)
        elif line.instruction == 'MULTIPLY': 
            state.accumulator *= get_real_value(variables, line.operand)
        elif line.instruction == 'DIVIDE': 
            state.accumulator /= get_real_value(variables, line.operand)
        elif line.instruction == 'JUMP':
            state.instruction_ptr = labels[line.operand]
            continue
        elif line.instruction == 'JIZERO':
            if state.accumulator == 0:
                state.instruction_ptr = labels[line.operand]
                continue
        elif line.instruction == 'JINEG':
            if state.accumulator < 0:
                state.instruction_ptr = labels[line.operand]
                continue
        elif line.instruction == 'RETURN':
            state.instruction_ptr = state.call_stack.pop()
        elif line.instruction == 'JUMPSR':
            state.call_stack.append(state.instruction_ptr)
            state.instruction_ptr = labels[line.operand]
            continue
        elif line.instruction == 'JSIZERO':
            if state.accumulator == 0:
                state.call_stack.append(state.instruction_ptr)
                state.instruction_ptr = labels[line.operand]
                continue
        elif line.instruction == 'JSINEG':
            if state.accumulator < 0:
                state.call_stack.append(state.instruction_ptr)
                state.instruction_ptr = labels[line.operand]
                continue
        elif line.instruction == 'POP':
            state.accumulator = state.stack.pop()
        elif line.instruction == 'PUSH':
            state.stack.append(state.accumulator)

        # If nothing else has changed the execution path, move to the
        # next instruction
        state.instruction_ptr += 1

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

# Debug Output
def debug_out(level, program, state):

    # Summary Output
    if level == 1 or level == 2:
        # Code Line, accumulator value, top stack value
        line = program.program_lines[state.instruction_ptr]
        label = str(line.label if line.label is not None else '')
        if line.operand is None:
            operand = ''
        elif line.instruction == 'PRINT':
            operand = '"{0}"'.format(line.operand)
        else:
            operand = line.operand

        if len(state.stack) > 0:
            top_of_stack = str(state.stack[len(state.stack)-1])
        else:
            top_of_stack = 'Empty'

        ## Accumulator State Flag (ZERO, NEG or none)
        flags = ''
        if state.accumulator == 0:
            flags = 'ZERO'
        elif state.accumulator < 0:
            flags = 'NEG'
    
        summary_format = ' [Accumlator: {0:>10}] [Flags: {1:>4}]'
        summary_format += ' [Stack Top: {2:>10s}]'
        summary_format += ' -> {3:<8}{4:<8} {5}'
        print('\nDEBUG:')
        print(summary_format.format(state.accumulator, flags, top_of_stack,
              label, line.instruction, operand))
               
    # Verbose output
    if level == 3 or level == 4:
        ouput_stack_variable_detail(program, state)

    if level == 2 or level == 4:
        input('Press [Enter] to EXECUTE this line.\n')
        pass

# Outputs details for STACK and VARIABLE values.
def ouput_stack_variable_detail(program, state):         
    print(' STACK (Top-Down)                   VARIABLES')
    print(' (Top-Down)                Name   | Value   ')

    # Which list has more items in it, the stack or the variable list?
    longest_list = max(len(state.stack), len(program.variables))
    index = 0
    while index < longest_list:
        stack_item = ''
        variable_name = ''
        variable_value = ''

        # Do current stack item, if there is one.
        if index < len(state.stack):
            stack_item = state.stack[(len(state.stack) - index) - 1]
       
        # Do next variable, if there is one.
        if index < len(program.variables):
            variable_name = list(program.variables)[index - 1]
            variable_value = program.variables[variable_name]
       
        line_fmt = '  {0:>8}'
        if variable_name != '': line_fmt += '                 {1:<6} = {2:>8}'
        
        print(line_fmt.format( stack_item, variable_name, variable_value))

        index += 1            
    
# Run!
if __name__ == '__main__':
    cesilplus() 
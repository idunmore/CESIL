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

@click.command()
@click.option('-i', '--input',
    type=click.Choice(['t', 'text', 'c', 'card'], case_sensitive=False),
    default='text', show_default=True, help='Text or punched Card input.')
@click.option('-d', '--debug',
    type=click.Choice(['0', '1', '2'], case_sensitive=False),
        default='0', show_default=True, help='Debug mode/verbosity level.')
@click.option('-p', '--plus', is_flag=True, default=False,
    help='Enables "plus" mode language extensions.')
@click.version_option('0.1.0')
@click.argument('source_file')
def cesilplus(input, debug, plus, source_file):
    """CESILPlus - CESIL Interpreter (w/ optional language extentions).
    
    \b
      CESIL: Computer Eduction in Schools Instruction Language

      "Plus" language extensions add a STACK to the language, enabled
    with the -p | --plus options.  Extensions are DISABLED by default.

      Extension instructions: PUSH, POP

    \b
        PUSH       - Pushes ACCUMULATOR value on to STACK
        PUSH 0     - Pushes LITERAL value on to STACK
        PUSH VAR   - Pushes VARIABLE value on to STACK
    \b
        POP        - Pops top value from STACK into the ACCUMULATOR
        POP VAR    - Pops top value from STACK into VARIABLE      
    """
    pass

def is_comment(line):
    return len(line) > 0 and line[0] in COMMENT_PREFIX

def is_legal_indentifier(identifier):
    return re.fullmatch(IDENTIFIER_PATTERN, identifier) is not None

def is_legal_integer(value):
    try:
        num = int(value)
        return (num >= VALUE_MIN and num <= VALUE_MAX)
    except:
        return False

def is_data_start(line):
    return len(line) > 0 and line[0] == START_DATA_SECTION

# Run!
if __name__ == '__main__':
    cesilplus() 
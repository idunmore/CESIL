# CESIL Plus - Computer Education in Schools Instruction Lanaguage
#              Interpreter w/ optional Extensions
#
# Author : Ian Michael Dunmore
# Date   : 05/02/2020
#
# License: https://github.com/idunmore/CESIL/blob/master/LICENSE

import enum
import click


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

# Run!
if __name__ == '__main__':
    cesilplus() 
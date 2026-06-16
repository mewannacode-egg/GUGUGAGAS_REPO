# Custom Python REPL
import readline
from os import getcwd, system, environ
from datetime import datetime
from requests import get
from difflib import get_close_matches

def perror(errType, err=None, nl=False, b='[Error]'):
    print(f"{'\n' if nl else ''}\033[1;31m -> {b} \033[0m- \033[1;33m{errType} \033[0m{f'| {err}' if err else ''}")

def pmsg(msg, col='\033[1;92m', b='[Help]'):
    print(f"{col} -> {b} \033[0m- {msg}")

def pmsginput(msg, col='\033[1;92m', b='[Stuff]'):
    return input(f"{col} -> {b} \033[0m- {msg}")

def main(x='>>> ', bufferMode='... ', prefix=':'):
    cmd = input(x)

    # Commands (prefix: ':')
    if cmd.startswith(prefix):
        arg1 = cmd[1:].strip()

        if arg1.startswith('??'):
            pmsg('User-Defined Variables ( Excludes internals, eg. __var__ )', b='MCommand')
            found_vars = False
            for key, val in globals().items():
                if key.startswith('_'):
                    continue
                if key in ['main', 'perror', 'pmsg', 'pmsginput', 'readline', 'environ', 'get', 'system', 'getcwd', 'datetime', 'get_close_matches']:
                    continue
                if hasattr(val, '__module__') and val.__module__ in ['builtins', 'os', 'datetime', 'requests', 'difflib']:
                    continue
                
                print(f"\033[1;92m -> \033[0m{key} = {val}")
                found_vars = True
            if not found_vars:
                perror('404', "Seems like you haven't defined any variables yet!")
        
        elif arg1 == 'clear' or arg1 == 'cls':
            system('clear')
            pmsg('Your terminal has been washed!', b='[MCommand]')

        # Location!
        elif arg1 in ['pwd', 'whereami', 'whatsmyip', 'ip?', 'ip', 'whaysmyip?']:
            cwd = getcwd()
            if arg1 == 'pwd':
                pmsg(cwd, b='[MCommand]')

            elif arg1 == 'whereami':
                pmsg(f"You are at '{cwd}'", b='[MCommand]')

            else:
                public_ip = get('https://api.ipify.org', timeout=3).text
                pmsg(f"Your public IP is '{public_ip}'", b='[MCommand]')

        elif arg1.startswith('exec '):
            system_cmd = arg1[5:].strip()

            # The "Don't be an idiot" filters
            blacklist = ['rm ', 'mv ', 'dd ', 'mkfs ', 'chmod 777 ']

            if any(forbidden in system_cmd for forbidden in blacklist):
                perror('Safety', f"Command '{system_cmd}' blocked because reasons! Use exec7 to bypass it")
            else:
                system(system_cmd)

        elif arg1.startswith('exec7 '):
            system(arg1[6:].strip())

        elif arg1 in ['whatsthetime?', 'whatsthetime', 'time']:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if arg1 == 'time':
                pmsg(f'[{now}]', b='[MCommand]')

            else:
                pmsg(f'Its currently [{now}]!', b='[MCommand]')

        elif arg1 == 'CRALIAS':
            from os import environ, path
            
            shell = environ.get("SHELL", "")
            shell_file = path.expanduser("~/.zshrc") if 'zsh' in shell else path.expanduser("~/.bashrc")
            
            if not path.exists(shell_file):
                perror('EnvError', f"Could not find configuration file at {shell_file}")
                return

            with open(shell_file, 'r') as f:
                if 'alias mpython=' in f.read():
                    perror('AliasExists', "The alias already exists in your shell config. Call 'mpython' to run the REPL")
                    return

            script_path = "/home/i_dont_use_arch_btw/IMPORTANT/REPL/mpython.py"
            alias_cmd = f'\nalias mpython="python3 {script_path}"\n'

            with open(shell_file, 'a') as f:
                f.write(alias_cmd)
                
            pmsg(f"Alias added to {shell_file}! Run 'source {shell_file}' or restart terminal, and call 'mpython' to run the REPL", b='[MCommand]')

        elif not arg1:
            perror('Empty command', f"Cannot execute an empty command!")

        else:
            valid_commands = ['CRALIAS', '??', 'clear', 'cls', 'pwd', 'whereami', 'whatsmyip', 'ip?', 'ip', 'exec', 'exec7', 'whatsthetime?', 'time']
            matches = get_close_matches(arg1, valid_commands, n=1, cutoff=0.6)
            
            perror('Unknown command', f"The command '{arg1}' hasn't been implemented yet!")
            
            if matches:
                pmsg(f"Did you mean '\033[1m{matches[0]}\033[0m'?", col='\033[1;33m')
        return

    
    # Multiline mode!
    if cmd.strip().endswith(':'):
        buffer = [cmd]
        
        while True:
            # Let the user control their own spacing completely!
            indent_cmd = input(bufferMode)
            
            # If they hit Enter on a completely blank line, we are done.
            if indent_cmd.strip() == '':
                break
                
            buffer.append(indent_cmd)

        cmd = '\n'.join(buffer)
        
        try:
            exec(cmd, globals())
        except Exception as e:
            perror(type(e).__name__, e)
        return
    
    # Single line 
# --- Single line execution logic ---
    try:
        # 1. Try to execute it as code (handles assignments like x = 7)
        exec(cmd, globals())
    except Exception:
        # 2. If it fails, try to evaluate it as an expression (handles 2+2)
        try:
            result = eval(cmd, globals())
            if result is not None:
                print(result)
        except (SyntaxError, NameError) as e:
            # 3. If both fail, run your suggestion logic
            suggestions = list(globals().keys()) + dir(__builtins__)
            msg = str(e)
            match = None
            
            if "name '" in msg:
                bad_name = msg.split("'")[1]
                matches = get_close_matches(bad_name, suggestions, n=1, cutoff=0.7)
                if matches:
                    match = matches[0]
            
            perror(type(e).__name__, e)
            if match:
                pmsg(f"Did you mean '\033[1m{match}\033[0m'?", col='\033[1;33m')

while True:
    try:
         main('\033[1;92m[MPython]\033[0m ', '\033[1;92m[MBuffer]\033[0m ')
    except KeyboardInterrupt as e:
        perror(f"{type(e).__name__}", nl=True)
        pmsg('Use exit() to quit instead', '\033[1;32m')
    except Exception as e:
        perror(type(e).__name__, e)

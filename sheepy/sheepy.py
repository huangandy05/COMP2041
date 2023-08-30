#!/usr/bin/env python3

# Note: my code accounts for many edge cases like
# echo "$1$#$a,random var${a}`pwd`$(pwd)"
# This is done using complicated stack and hence the long code..

import sys, re, keyword, builtins

# Function to check if variable is a python keyword or builtin
def to_python_var(var):
    if var in keyword.kwlist or var in dir(builtins):
        return var + '_'
    else:
        return var
    
def check_python_var(var):
    return var in keyword.kwlist or var in dir(builtins)


def shell_to_python(shell_script):
    # Global variables and imports
    imports = []
    variables = {}
    currIndent = 0
    use_flatten_helper = False
    first_case_line = True

    # Helper variables
    flatten_nested_array_str = '''\ndef flatten_nested_array(arr):
    result = []
    for item in arr:
        if isinstance(item, list):
            result.extend(flatten_nested_array(item))
        else:
            result.append(item)
    return result\n'''
    
    ### Helper functions ###
    def add_import(import_name):
        if import_name not in imports:
            imports.append(import_name)

    def check_for_variables(string):
        # Check contains $ or ``
        if re.search(r"[^\\]\$", string) or re.search(r"[^\\]`", string):
            return True
        else:
            return False

    # Functions to substitute variables
    # $1, $2, $3,...
    def var_sub_command_line_arg(str):
        add_import('sys')
        return re.sub(r"\$(\d)", r"{sys.argv[\1]}", str)
    
    # $@
    def var_sub_command_args(str):
        add_import('sys')
        return re.sub(r"\$@", "{' '.join(sys.argv[1:])}", str)

    # $#
    def var_sub_num_args(str):
        add_import('sys')
        return re.sub(r"\$#", "{len(sys.argv[1:])}", str)
    
    # ${expr}
    def var_sub_var_val(str):
        return re.sub(r"\$\{([^}]*)\}", r"{\1}", str)
    
    # Arithmetic expression $((expr)) (simple version)
    def convert_arithmetic_expr(expr):
        return re.sub(r"[a-zA-Z]+\w*", r"int(\g<0>)", expr)
    def var_sub_arith_expr(str):
        matches = re.findall(r"\$\(\([^)]*\)\)", str)
        new_expr = str
        for match in matches:
            new = '{' + convert_arithmetic_expr(match)[3:-2] + '}'
            new_expr = new_expr.replace(match, new, 1)

        return new_expr
    
    # Command substitution backticks ``
    def convert_backtick(string):
        add_import('subprocess')
        stripped_line = string[1:-1]
        list_of_args, comment = str_to_array(stripped_line)
        return f"subprocess.run({list_of_args}, text=True, stdout=subprocess.PIPE).stdout.strip()"
    def var_sub_backticks(str):
        matches = re.findall(r"`[^`]*`", str)
        new_expr = str
        for match in matches:
            new = '{' + convert_backtick(match) + '}'
            new_expr = new_expr.replace(match, new, 1)
        return new_expr
    
    # Helper function that matches a nested $()
    def match_balanced_command_sub(s):
        start = -1
        counter = 0
        max_expr = ""
        max_length = 0

        i = 0
        while i < len(s):
            if s[i:i+2] == '$(':
                counter += 1
                if start == -1:
                    start = i
                i += 1  # Skip the next character as we've matched two characters
            elif s[i] == ')' and counter > 0:
                counter -= 1
                if counter == 0:
                    if i - start + 1 > max_length:
                        max_length = i - start + 1
                        max_expr = s[start:i+1]
                    start = -1
            i += 1

        return max_expr

    
    # Command substitution $() input in the form $(expr)
    def convert_command_sub(string):
        add_import('subprocess')
        stripped_line = string[2:-1]
        list_of_args, comment = str_to_array(stripped_line)
        return f"subprocess.run({list_of_args}, text=True, stdout=subprocess.PIPE).stdout.strip()"
    def var_sub_command_sub(string):
        while match_balanced_command_sub(string):
            match = match_balanced_command_sub(string)
            string = string.replace(match, '{' + convert_command_sub(match) + '}', 1)
        return string

    def var_sub_str(str):
        return re.sub(r"\$([a-zA-Z_][\w_]*)", r"{\1}", str)

    
    # Function to convert expr to python given single quotes, double quotes, $, etc
    def convert_expr(expr):
        rest_of_line = expr.strip()
        var_str_parts = []
        use_f_string = False
        comment = ""

        while rest_of_line:
            # single quotes
            if re.match(r"'[^']*'", rest_of_line):
                match = re.match(r"^'[^']*'", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                var_str_parts.append(match.group()[1:-1])
            # double quotes
            elif re.match(r'"[^"]*"', rest_of_line):
                match = re.match(r'"[^"]*"', rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                # Check if there are variables in the string, if so, use f-string
                if check_for_variables(match.group()):
                    use_f_string = True
                    string = var_sub_command_line_arg(match.group()[1:-1])
                    string = var_sub_command_args(string)
                    string = var_sub_num_args(string)
                    string = var_sub_var_val(string)
                    string = var_sub_arith_expr(string)
                    string = var_sub_str(string)
                    string = var_sub_backticks(string)
                    string = var_sub_command_sub(string)
                    var_str_parts.append(string)
                else:
                    var_str_parts.append(match.group()[1:-1])
            # Comment
            elif re.match(r"\s+#.*", rest_of_line):
                match = re.match(r"\s+#.*", rest_of_line)
                # rest_of_line = rest_of_line[match.end():]
                comment = match.group().strip()
                break
            # Command line argument numbers $1, $2, $3,...
            elif re.match(r"\$\d", rest_of_line):
                match = re.match(r"\$\d", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('sys')
                use_f_string = True
                var_str_parts.append(var_sub_command_line_arg(match.group()))
            # Number of command line args $#
            elif re.match(r"\$#", rest_of_line):
                match = re.match(r"\$#", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('sys')
                use_f_string = True
                var_str_parts.append(var_sub_num_args(match.group()))
            # List command line args $@
            elif re.match(r"\$@", rest_of_line):
                match = re.match(r"\$@", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('sys')
                use_f_string = True
                var_str_parts.append(var_sub_command_args(match.group()))
            # Variable ${}
            elif re.match(r"\$\{[^}]*\}", rest_of_line):
                match = re.match(r"\$\{[^}]*\}", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                use_f_string = True
                var_str_parts.append(var_sub_var_val(match.group()))
            # Arithmetic expression $(())
            elif re.match(r"\$\(\([^)]*\)\)", rest_of_line):
                match = re.match(r"\$\(\([^)]*\)\)", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                use_f_string = True
                new_expr = convert_arithmetic_expr(match.group()[3:-2])
                var_str_parts.append("{" + new_expr + "}")
            # Command substitution backticks ``
            elif re.match(r"`[^`]*`", rest_of_line):
                match = re.match(r"`[^`]*`", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                add_import('subprocess')
                use_f_string = True
                var_str_parts.append('{' + convert_backtick(match.group()) + '}')
            # Command substitution $()
            elif re.match(r"\$\([^\(]", rest_of_line):
                match = match_balanced_command_sub(rest_of_line)
                rest_of_line = rest_of_line[len(match):]
                use_f_string = True
                var_str_parts.append('{' + convert_command_sub(match) + '}')

            # Variable sub $var
            elif re.match(r"\$[a-zA-Z_][\w_]*", rest_of_line):
                match = re.match(r"\$[a-zA-Z_][\w_]*", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                use_f_string = True
                # var_str_parts.append(re.sub(r"\$([a-zA-Z_][\w_]*)", r"{\1}", match.group()))
                var_str_parts.append(var_sub_str(match.group()))
            # Globbing
            elif re.match(r"[^\s]*[\*\?\[\]]+[^\s]*", rest_of_line):
                match = re.match(r"[^\s]*[\*\?\[\]]+[^\s]*", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('glob')
                use_f_string = True
                var_str_parts.append("{' '.join(sorted(glob.glob('" + match.group() + "')))}")
            # normal word (everything else)
            elif re.match(r"[^\$\(\) ]+", rest_of_line):
                match = re.match(r"[^\$\(\) ]+", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                var_str_parts.append(match.group())
            else:
                print('no match')
                break
        
        # Concatenate and return
        # doesn't account for x='""'
        full_string = "".join(var_str_parts)
        if use_f_string:
            return(f"f\"{full_string}\"")
        else:
            return(f"\"{full_string}\"")

    # Function to clean python keywords and vars
    def check_python_keywords(line):
        # Search for any variables in the line and add _ at end
        new_line = line
        ## Variable assignent
        if re.match(r'[^= ]*=', new_line):
            match = re.match(r"^([^=]*)=", line).group(1)
            new_line = new_line.replace(match, to_python_var(match), 1)

        ## Variable assignment with $var (doesn't account for single quotes yet)
        variables = re.findall(r"\$[a-zA-Z_][\w]*", new_line)
        for var in variables:
            new_line = new_line.replace(var, f"${to_python_var(var[1:])}")

        ## Variable assignment iwth ${var}
        variables = re.findall(r"\${[a-zA-Z_][\w]*}", new_line)
        for var in variables:
            new_line = new_line.replace(var, f"${'{'}{to_python_var(var[2:-1])}{'}'}")
        return new_line
            

    # Function that takes in echo line
    def transpile_echo(line):
        # Get the rest of the line
        rest_of_line = line[5:].strip()
        
        has_n_flag = False
        # Check for -n option
        if rest_of_line[:3] == '-n ':
            has_n_flag = True
            rest_of_line = rest_of_line[3:].strip()
        
        print_string = [] # this will be concatenated to form the 'print()' string
        use_f_string = False # Set to true if echo contains $_, ``
        comment = "" # If a comment exists, it will be stored here
        
        # Check for comment (echo # smt)
        if rest_of_line[0] == '#':
            comment = rest_of_line
            rest_of_line = ""

        # Next, we process each argument one by one
        while rest_of_line:
            # Single quote
            if re.match(r"'[^']*'", rest_of_line):
                match = re.match(r"^'[^']*'", rest_of_line)
                # Convert double quotes to \"
                rest_of_line = rest_of_line[match.end():]

                string = re.sub(r'"', '\\\"', match.group()[1:-1])
            
                print_string.append(string)
            # Double quotes
            elif re.match(r'"[^"]*"', rest_of_line):
                match = re.match(r'"[^"]*"', rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                # Check if there are variables in the string, if so, use f-string
                if check_for_variables(match.group()):
                    use_f_string = True
                    string = var_sub_command_line_arg(match.group()[1:-1])
                    string = var_sub_command_args(string)
                    string = var_sub_num_args(string)
                    string = var_sub_var_val(string)
                    string = var_sub_arith_expr(string)
                    string = var_sub_str(string)
                    string = var_sub_backticks(string)
                    string = var_sub_command_sub(string)
                    print_string.append(string)
                else:
                    print_string.append(match.group()[1:-1])
            # Comment
            elif re.match(r"\s+#.*", rest_of_line):
                match = re.match(r"\s+#.*", rest_of_line)
                # rest_of_line = rest_of_line[match.end():]
                comment = match.group().strip()
                break
            # Remove duplicate spaces
            elif re.match(r"\s+", rest_of_line):
                match = re.match(r"\s+", rest_of_line)
                rest_of_line = rest_of_line.strip()

                print_string.append(' ')
            # Command line argument numbers $1, $2, $3,...
            elif re.match(r"\$\d", rest_of_line):
                match = re.match(r"\$\d", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('sys')
                use_f_string = True
                print_string.append(var_sub_command_line_arg(match.group()))
            # Number of command line args $#
            elif re.match(r"\$#", rest_of_line):
                match = re.match(r"\$#", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('sys')
                use_f_string = True
                print_string.append(var_sub_num_args(match.group()))
            # List command line args $@
            elif re.match(r"\$@", rest_of_line):
                match = re.match(r"\$@", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('sys')
                use_f_string = True
                print_string.append("{' '.join(' '.join(sys.argv[1:]).split())}")
            # Variable ${}
            elif re.match(r"\$\{[^}]*\}", rest_of_line):
                match = re.match(r"\$\{[^}]*\}", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                use_f_string = True
                print_string.append(var_sub_var_val(match.group()))
            # Arithmetic expression $(())
            elif re.match(r"\$\(\([^)]*\)\)", rest_of_line):
                match = re.match(r"\$\(\([^)]*\)\)", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                use_f_string = True
                new_expr = convert_arithmetic_expr(match.group()[3:-2])
                print_string.append("{" + new_expr + "}")
            # Command substitution backticks ``
            elif re.match(r"`[^`]*`", rest_of_line):
                match = re.match(r"`[^`]*`", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                add_import('subprocess')
                use_f_string = True
                print_string.append('{' + convert_backtick(match.group()) + '}')
            # Command substitution $()
            elif re.match(r"\$\(", rest_of_line):
                match = match_balanced_command_sub(rest_of_line)
                rest_of_line = rest_of_line[len(match):]
                use_f_string = True
                print_string.append('{' + convert_command_sub(match) + '}')

            # Variable sub $var
            elif re.match(r"\$[a-zA-Z_][\w_]*", rest_of_line):
                match = re.match(r"\$[a-zA-Z_][\w_]*", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                use_f_string = True
                print_string.append(var_sub_str(match.group()))
            # Globbing
            elif re.match(r"[^\s]*[\*\?\[\]]+[^\s]*", rest_of_line):
                match = re.match(r"[^\s]*[\*\?\[\]]+[^\s]*", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('glob')
                use_f_string = True
                print_string.append("{' '.join(sorted(glob.glob('" + match.group() + "')))}")
            # normal word (everything else)
            elif re.match(r"[^\$\(\) ]+", rest_of_line):
                match = re.match(r"[^\$\(\) ]+", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                print_string.append(match.group())
            else:
                print('no match')
                break

        # Concatenate and return the print statement
        full_string = "".join(print_string)
        # -n option
        n_flag_str = ""
        if has_n_flag:
            n_flag_str += ', end=""'
        
        # Doesn't account for echo '""'
        if use_f_string:
            return(f"print(f\"{full_string}\"{n_flag_str}) {comment}")
        else:
            return(f"print(\"{full_string}\"{n_flag_str}) {comment}")

    def transpile_variable_assignment(line):
        matches = re.match('^([^=]*)=(.*)', line)
        var_name = matches.group(1)
        rest_of_line = matches.group(2)

        var_str_parts = []
        use_f_string = False
        comment = ""

        while rest_of_line:
            # single quotes
            if re.match(r"'[^']*'", rest_of_line):
                match = re.match(r"^'[^']*'", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                var_str_parts.append(match.group()[1:-1])
            # double quotes
            elif re.match(r'"[^"]*"', rest_of_line):
                match = re.match(r'"[^"]*"', rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                # Check if there are variables in the string, if so, use f-string
                if check_for_variables(match.group()):
                    use_f_string = True
                    string = var_sub_command_line_arg(match.group()[1:-1])
                    string = var_sub_command_args(string)
                    string = var_sub_num_args(string)
                    string = var_sub_var_val(string)
                    string = var_sub_arith_expr(string)
                    string = var_sub_str(string)
                    string = var_sub_backticks(string)
                    string = var_sub_command_sub(string)
                    var_str_parts.append(string)
                else:
                    var_str_parts.append(match.group()[1:-1])
            # Comment
            elif re.match(r"\s+#.*", rest_of_line):
                match = re.match(r"\s+#.*", rest_of_line)
                # rest_of_line = rest_of_line[match.end():]
                comment = match.group().strip()
                break
            # Command line argument numbers $1, $2, $3,...
            elif re.match(r"\$\d", rest_of_line):
                match = re.match(r"\$\d", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('sys')
                use_f_string = True
                var_str_parts.append(var_sub_command_line_arg(match.group()))
            # Number of command line args $#
            elif re.match(r"\$#", rest_of_line):
                match = re.match(r"\$#", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('sys')
                use_f_string = True
                var_str_parts.append(var_sub_num_args(match.group()))
            # List command line args $@
            elif re.match(r"\$@", rest_of_line):
                match = re.match(r"\$@", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('sys')
                use_f_string = True
                var_str_parts.append(var_sub_command_args(match.group()))
            # Variable ${}
            elif re.match(r"\$\{[^}]*\}", rest_of_line):
                match = re.match(r"\$\{[^}]*\}", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                use_f_string = True
                var_str_parts.append(var_sub_var_val(match.group()))
            # Arithmetic expression $(())
            elif re.match(r"\$\(\([^)]*\)\)", rest_of_line):
                match = re.match(r"\$\(\([^)]*\)\)", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                use_f_string = True
                new_expr = convert_arithmetic_expr(match.group()[3:-2])
                var_str_parts.append("{" + new_expr + "}")
            # Command substitution backticks ``
            elif re.match(r"`[^`]*`", rest_of_line):
                match = re.match(r"`[^`]*`", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                add_import('subprocess')
                use_f_string = True
                var_str_parts.append('{' + convert_backtick(match.group()) + '}')
            # Command substitution $()
            elif re.match(r"\$\([^\(]", rest_of_line):
                match = match_balanced_command_sub(rest_of_line)
                rest_of_line = rest_of_line[len(match):]
                use_f_string = True
                var_str_parts.append('{' + convert_command_sub(match) + '}')

            # Variable sub $var
            elif re.match(r"\$[a-zA-Z_][\w_]*", rest_of_line):
                match = re.match(r"\$[a-zA-Z_][\w_]*", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                use_f_string = True
                var_str_parts.append(var_sub_str(match.group()))
            # Globbing
            elif re.match(r"[^\s]*[\*\?\[\]]+[^\s]*", rest_of_line):
                match = re.match(r"[^\s]*[\*\?\[\]]+[^\s]*", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('glob')
                use_f_string = True
                var_str_parts.append("{' '.join(sorted(glob.glob('" + match.group() + "')))}")
            # normal word (everything else)
            elif re.match(r"[^\$\(\) ]+", rest_of_line):
                match = re.match(r"[^\$\(\) ]+", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                var_str_parts.append(match.group())
            else:
                print('no match')
                break
        
        # Concatenate and return
        # doesn't account for x='""'
        full_string = "".join(var_str_parts)
        if use_f_string:
            return(f"{var_name} = f\"{full_string}\" {comment}")
        else:
            return(f"{var_name} = \"{full_string}\" {comment}")
        
    def transpile_for(line):
        variable = line.split()[1]
        rest_of_line = re.sub(r'^(\s*\S+){3}\s*', '', line)
        use_flatten_func = False
        comment = ""
        args = []
        currArg = ""
        use_f_str = False

        def add_to_arg():
            nonlocal args
            nonlocal currArg
            nonlocal use_f_str
            if use_f_str:
                args.append(f'f"{currArg}"')
            else:
                args.append(f"'{currArg}'")
            currArg = ""
            use_f_str = False

        while rest_of_line:
            # single quotes
            if re.match(r"'[^']*'", rest_of_line):
                match = re.match(r"^'[^']*'", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                currArg += f"{match.group()[1:-1]}"
            # double quotes
            elif re.match(r'"[^"]*"', rest_of_line):
                match = re.match(r'"[^"]*"', rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                # Check if there are variables in the string, if so, use f-string
                if check_for_variables(match.group()):
                    use_f_str = True
                    string = var_sub_command_line_arg(match.group()[1:-1])
                    string = var_sub_command_args(string)
                    string = var_sub_num_args(string)
                    string = var_sub_var_val(string)
                    string = var_sub_arith_expr(string)
                    string = var_sub_str(string)
                    string = var_sub_backticks(string)
                    string = var_sub_command_sub(string)
                    currArg += string
                else:
                    currArg += match.group()[1:-1]
            # Comment
            elif re.match(r"\s+#.*", rest_of_line):
                match = re.match(r"\s+#.*", rest_of_line)
                comment = match.group().strip()
                break
            elif re.match(r"\s+", rest_of_line):
                match = re.match(r"\s+", rest_of_line)
                rest_of_line = rest_of_line.strip()
                add_to_arg()
            # Command line argument numbers $1, $2, $3,...
            elif re.match(r"\$\d", rest_of_line):
                match = re.match(r"\$\d", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('sys')
                use_f_str = True

                currArg += var_sub_command_line_arg(match.group())
            # Number of command line args $#
            elif re.match(r"\$#", rest_of_line):
                match = re.match(r"\$#", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('sys')
                use_f_str = True
                currArg += var_sub_num_args(match.group())
            # List command line args $@
            elif re.match(r"\$@", rest_of_line):
                match = re.match(r"\$@", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('sys')
                use_flatten_func = True
                args.append("' '.join(sys.argv[1:]).split()")
                currArg = ""
                use_f_str = False
            # Variable ${}
            elif re.match(r"\$\{[^}]*\}", rest_of_line):
                match = re.match(r"\$\{[^}]*\}", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                use_f_str = True
                currArg += var_sub_var_val(match.group())
            # Arithmetic expression $(())
            elif re.match(r"\$\(\([^)]*\)\)", rest_of_line):
                match = re.match(r"\$\(\([^)]*\)\)", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                use_f_str = True
                new_expr = convert_arithmetic_expr(match.group()[3:-2])
                currArg += "{" + new_expr + "}"
            # Command substitution backticks ``
            elif re.match(r"`[^`]*`", rest_of_line):
                match = re.match(r"`[^`]*`", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                add_import('subprocess')
                use_f_str = True
                currArg += '{' + convert_backtick(match.group()) + '}'
            # Command substitution $()
            elif re.match(r"\$\([^\(]", rest_of_line):
                match = match_balanced_command_sub(rest_of_line)
                rest_of_line = rest_of_line[len(match):].strip()
                args.append(f"{convert_command_sub(match)}")
                currArg = ""
                use_f_str = False

            # Variable sub $var
            elif re.match(r"\$[a-zA-Z_][\w_]*", rest_of_line):
                match = re.match(r"\$[a-zA-Z_][\w_]*", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                use_f_str = True
                currArg += var_sub_str(match.group())
            # Globbing
            elif re.match(r"[^\s]*[\*\?\[\]]+[^\s]*", rest_of_line):
                match = re.match(r"[^\s]*[\*\?\[\]]+[^\s]*", rest_of_line)
                rest_of_line = rest_of_line[match.end():].strip()

                add_import('glob')
                use_flatten_func = True
                args.append("sorted(glob.glob('" + match.group() + "'))")
                currArg = ""
                use_f_str = False
            # normal word (everything else)
            elif re.match(r"[^\$\(\) ]+", rest_of_line):
                match = re.match(r"[^\$\(\) ]+", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                currArg += match.group()
            else:
                print('no match')
                break

        if currArg != "":
            add_to_arg()

        args_str = ', '.join(args)

        if use_flatten_func:
            nonlocal use_flatten_helper
            use_flatten_helper = True
            return f"for {variable} in flatten_nested_array([{args_str}]): {comment}"
        else:
            return f"for {variable} in [{args_str}]: {comment}"
        
    
    def transpile_exit(line):
        add_import('sys')
        return re.sub(r"exit\s+(\d*)(.*)", r"sys.exit(\1) \2", line)

    def transpile_cd(line):
        add_import('os')
        # should handle comments aye
        return re.sub(r"cd\s+([^ ]*)(.*)", r'os.chdir("\1") \2', line)
    
    def transpile_read(line):
        rest_of_line = line[5:].strip()
        variables = rest_of_line.split()
        # check for python keywords and add _ at end
        for var in variables:
            if check_python_var(var):
                variables[variables.index(var)] = var + '_'

        comments = ""
        # Remove and store comments
        for ind, var in enumerate(variables):
            if var.startswith('#'):
                comments = ' '.join(variables[ind:])
                variables = variables[:ind]
                break

        # One variable (read var)
        if len(variables) == 1:
            return f"{variables[0]} = input() {comments}"
        # Multiple variables read var1 var2 var3
        else:
            tabs = '\t' * currIndent
            return f"{', '.join(variables[:-1])}, *{variables[-1]} = input().split() {comments}\n{tabs}{variables[-1]} = ' '.join({variables[-1]})"
        
    # Take in a string and separates it into an array
    def str_to_array(line):
        rest_of_line = line.strip()
        use_flatten_func = False
        comment = ""
        args = []
        currArg = ""
        use_f_str = False

        def add_to_arg():
            nonlocal args
            nonlocal currArg
            nonlocal use_f_str
            if use_f_str:
                args.append(f"f'{currArg}'")
            else:
                args.append(f"'{currArg}'")
            currArg = ""
            use_f_str = False

        while rest_of_line:
            # single quotes
            if re.match(r"'[^']*'", rest_of_line):
                match = re.match(r"^'[^']*'", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                currArg += f"{match.group()[1:-1]}"
            # double quotes
            elif re.match(r'"[^"]*"', rest_of_line):
                match = re.match(r'"[^"]*"', rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                # Check if there are variables in the string, if so, use f-string
                if check_for_variables(match.group()):
                    use_f_str = True
                    string = var_sub_command_line_arg(match.group()[1:-1])
                    string = var_sub_command_args(string)
                    string = var_sub_num_args(string)
                    string = var_sub_var_val(string)
                    string = var_sub_arith_expr(string)
                    string = var_sub_str(string)
                    string = var_sub_backticks(string)
                    string = var_sub_command_sub(string)                    
                    currArg += string
                else:
                    currArg += match.group()[1:-1]
            # Comment
            elif re.match(r"\s+#.*", rest_of_line):
                match = re.match(r"\s+#.*", rest_of_line)
                comment = match.group().strip()
                break
            elif re.match(r"\s+", rest_of_line):
                match = re.match(r"\s+", rest_of_line)
                rest_of_line = rest_of_line.strip()
                add_to_arg()
            # Command line argument numbers $1, $2, $3,...
            elif re.match(r"\$\d", rest_of_line):
                match = re.match(r"\$\d", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('sys')
                use_f_str = True

                currArg += var_sub_command_line_arg(match.group())
            # Number of command line args $#
            elif re.match(r"\$#", rest_of_line):
                match = re.match(r"\$#", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('sys')
                use_f_str = True
                currArg += var_sub_num_args(match.group())
            # List command line args $@
            elif re.match(r"\$@", rest_of_line):
                match = re.match(r"\$@", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                add_import('sys')
                use_flatten_func = True
                args.append("' '.join(sys.argv[1:]).split()")
                currArg = ""
                use_f_str = False
            # Variable ${}
            elif re.match(r"\$\{[^}]*\}", rest_of_line):
                match = re.match(r"\$\{[^}]*\}", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                use_f_str = True
                currArg += var_sub_var_val(match.group())
            # Arithmetic expression $(())
            elif re.match(r"\$\(\([^)]*\)\)", rest_of_line):
                match = re.match(r"\$\(\([^)]*\)\)", rest_of_line)
                rest_of_line = rest_of_line[match.end():]

                use_f_str = True
                new_expr = convert_arithmetic_expr(match.group()[3:-2])
                currArg += "{" + new_expr + "}"
            # Command substitution backticks ``
            elif re.match(r"`[^`]*`", rest_of_line):
                match = re.match(r"`[^`]*`", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                add_import('subprocess')
                use_f_str = True
                currArg += '{' + convert_backtick(match.group()) + '}'
            # Command substitution $()
            elif re.match(r"\$\([^\(]", rest_of_line):
                match = match_balanced_command_sub(rest_of_line)
                rest_of_line = rest_of_line[len(match):].strip()
                args.append(f"{convert_command_sub(match)}")
                currArg = ""
                use_f_str = False

            # Variable sub $var
            elif re.match(r"\$[a-zA-Z_][\w_]*", rest_of_line):
                match = re.match(r"\$[a-zA-Z_][\w_]*", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                use_f_str = True
                currArg += var_sub_str(match.group())
            # Globbing
            elif re.match(r"[^\s]*[\*\?\[\]]+[^\s]*", rest_of_line):
                match = re.match(r"[^\s]*[\*\?\[\]]+[^\s]*", rest_of_line)
                rest_of_line = rest_of_line[match.end():].strip()

                add_import('glob')
                use_flatten_func = True
                args.append("sorted(glob.glob('" + match.group() + "'))")
                currArg = ""
                use_f_str = False
            # normal word (everything else)
            elif re.match(r"[^\$\(\) ]+", rest_of_line):
                match = re.match(r"[^\$\(\) ]+", rest_of_line)
                rest_of_line = rest_of_line[match.end():]
                currArg += match.group()
            else:
                print('no match')
                break

        if currArg != "":
            add_to_arg()

        args_str = ', '.join(args)

        if use_flatten_func:
            nonlocal use_flatten_helper
            use_flatten_helper = True
            return f"flatten_nested_array([{args_str}])", comment
        else:
            return f"[{args_str}]", comment
        

    # Transpile test and [] commands
    def transpile_test(line):

        # Split on && and ||
        split_line = re.split(r"\s*(?:&&|\|\|)\s*", line)
        # If split commands aren't test or [], use external command
        for command in split_line:
            if not re.match(r"\s*(?:test|\[|\])\s+", command):
                add_import('subprocess')
                list_of_args, comment = str_to_array(command)
                line = line.replace(command, f"not subprocess.run({list_of_args}).returncode", 1)

        # First, replace all instances of [ ] expressions
        matches = re.findall(r"\[\s.*?\s\]", line)
        for match in matches:
            line = line.replace(match, transpile_test_helper(match[1:-1].strip())) # Get rid of the square brackets

        # Replace all instances of test expressions
        pattern = r"\b(?:test)\s+.*?(?=(?:\s*&&|\s*\|\||\s*-o|\s*-a|$|\s+#))"
        matches = re.findall(pattern, line)
        for match in matches:
            line = line.replace(match, transpile_test_helper(match[5:].strip()))

        # Replace && and ||
        line = line.replace(' && ', ' and ')
        line = line.replace(' || ', ' or ')

        # Remove comment
        comment = ""
        if ' #' in line:
            comment = line[line.index(' #'):]
            line = line[:line.index(' #')].strip()

        return f"{line}: {comment}"


    def transpile_test_helper(expr):
        operators = {
            '-eq': '==',
            '-ne': '!=',
            '-gt': '>',
            '-ge': '>=',
            '-lt': '<',
            '-le': '<=',
            '!=': '!=',
            '=': '==',
        }
        # File or directory test
        if re.match(r"-[a-zA-Z]", expr):
            file_or_string = convert_expr(expr[3:].strip())
            add_import('os')
            # -d
            if expr.split()[0] == "-d":
                return f"os.path.isdir({file_or_string})"
            # -f
            if expr.split()[0] == "-f":
                return f"os.path.isfile({file_or_string})"
            # -r
            if expr.split()[0] == "-r":
                return f"os.access({file_or_string}, os.R_OK)"
            # -w
            if expr.split()[0] == "-w":
                return f"os.access({file_or_string}, os.W_OK)"
            # -x
            if expr.split()[0] == "-x":
                return f"os.access({file_or_string}, os.X_OK)"
            # -e
            if expr.split()[0] == "-e":
                return f"os.path.exists({file_or_string})"
            # -s
            if expr.split()[0] == "-s":
                return f"os.path.getsize({file_or_string}) > 0"
            
            # Check for string comparisons
            # -n
            if expr.split()[0] == "-n":
                return f"len({file_or_string}) > 0"
            # -z
            if expr.split()[0] == "-z":
                return f"len({file_or_string}) == 0"
        
        # Numeric comparison
        if re.search(r"\s+(?:-eq|-ne|-gt|-ge|-lt|-le)\s+", expr):
            matches = re.match(r"(.*)\s*((?:-eq|-ne|-gt|-ge|-lt|-le))\s*(.*)", expr)
            left = convert_expr(matches.group(1))
            operation = matches.group(2)
            right = convert_expr(matches.group(3))
            return f"int({left.strip()}) {operators[operation]} int({right})"

        # # String comparison: =, !=
        if re.search(r"\s*(?:!=|=)\s*", expr):
            matches = re.match(r"(.*)\s+((?:!=|=))\s*(.*)", expr)
            left = convert_expr(matches.group(1))
            operation = matches.group(2)
            right = convert_expr(matches.group(3))
            return f"{left.strip()} {operators[operation]} {right}"

        return 'hi'
    
    # Transpile case
    # case $var in becomes var = $var
    def transpile_case(line):
        match = re.match(r"case\s+(.*)\s+in", line)
        return f"CASE_VAR = {convert_expr(match.group(1))}"
    
    def transpile_case_option(line):
        # Check if there is | in the line
        if '|' in line:
            return f"CASE_VAR in [{', '.join([convert_expr(x) for x in line.split('|')])}]:"
        else:
            return f"CASE_VAR == {convert_expr(line)}:"

    python_script = ""

    for line in shell_script.split('\n'):
        # Remove whitespace at start and end of string
        stripped_line = line.strip()

        stripped_line = check_python_keywords(stripped_line)
        
        # Check for shebang -> do nothing
        if stripped_line.startswith('#!'):
            continue
        # Empty line -> append
        elif stripped_line == '':
            python_script += '\n'
            continue
        # Comment
        elif stripped_line.startswith('#'):
            python_script += '\t' * currIndent + stripped_line + '\n'
            continue
        # echo command
        elif stripped_line == 'echo' or stripped_line.startswith('echo '):
            # If empty echo, append empty print statement, check for comment also
            if len(stripped_line.split()) == 1:
                python_script += '\t' * currIndent + 'print()' + '\n'
            # Empty echo, but with comment
            elif re.match(r'echo\s+#', stripped_line):
                python_script += '\t' * currIndent + 'print()' + stripped_line[4:] + '\n'
            else:
                python_script += '\t' * currIndent + transpile_echo(stripped_line) + '\n'
        # Variable assignment
        elif re.match(r'[a-zA-Z_]+[\w_]*=', stripped_line):
            python_script += '\t' * currIndent + transpile_variable_assignment(stripped_line) + '\n'
        # For loop
        elif stripped_line.startswith('for '):
            python_script += '\t' * currIndent + transpile_for(stripped_line) + '\n'
            currIndent += 1
        # do (check for comment)
        elif stripped_line == 'do' or stripped_line.startswith('do '):
            if len(stripped_line.split()) > 1:
                python_script += '\t' * currIndent + stripped_line[3:].strip() + '\n'
        # done (check for comment)
        elif stripped_line == 'done' or stripped_line.startswith('done '):
            # Check for comment
            if len(stripped_line.split()) > 1:
                python_script += '\t' * currIndent + stripped_line[5:].strip() + '\n'
            currIndent -= 1
        # exit
        elif stripped_line == 'exit' or stripped_line.startswith('exit '):
            python_script += '\t' * currIndent + transpile_exit(stripped_line) + '\n'
        # cd
        elif stripped_line == 'cd' or stripped_line.startswith('cd '):
            python_script += '\t' * currIndent + transpile_cd(stripped_line) + '\n'
        # read
        elif stripped_line.startswith('read '):
            python_script += '\t' * currIndent + transpile_read(stripped_line) + '\n'
        # if statement
        elif stripped_line.startswith('if '):
            python_script += '\t' * currIndent + 'if ' + transpile_test(stripped_line[3:].strip()) + '\n'
            currIndent += 1
        # elif statement
        elif stripped_line.startswith('elif '):
            python_script += '\t' * (currIndent - 1) + 'elif ' + transpile_test(stripped_line[5:].strip()) + '\n'
        # else statement
        elif stripped_line == 'else' or stripped_line.startswith('else '):
            if len(stripped_line.split()) > 1:
                python_script += '\t' * (currIndent - 1) + 'else: ' + stripped_line[5:].strip() + '\n'
            else:
                python_script += '\t' * (currIndent - 1) + 'else:\n'
        # then statement
        elif stripped_line == 'then' or stripped_line.startswith('then '):
            if len(stripped_line.split()) > 1:
                python_script += '\t' * currIndent + stripped_line[5:].strip() + '\n'
        # fi statement
        elif stripped_line == 'fi':
            currIndent -= 1
        # while statement
        elif stripped_line.startswith('while '):
            python_script += '\t' * currIndent + 'while ' + transpile_test(stripped_line[6:].strip()) + '\n'
            currIndent += 1
        # case statement - treat it as a variable assignment
        elif stripped_line.startswith('case '):
            python_script += '\t' * currIndent + transpile_case(stripped_line) + '\n'
        # Case numbers - we pray that CASE_VAR isn't declared before this lolololololol
        elif re.match(r"[0-9*]+", stripped_line):
            # Check to use if or elif
            if first_case_line:
                first_case_line = False
                python_script += '\t' * currIndent + 'if ' + transpile_case_option(stripped_line[:-1]) + '\n'
                currIndent += 1
            elif stripped_line == '*)':
                python_script += '\t' * (currIndent - 1) + 'else:\n'
            else:
                python_script += '\t' * (currIndent - 1) + 'elif ' + transpile_case_option(stripped_line[:-1]) + '\n'
        # esac
        elif stripped_line == 'esac' or stripped_line.startswith('esac '):
            first_case_line = True
            currIndent -= 1
        # ;; then pass
        elif stripped_line == ';;' or stripped_line.startswith(';; '):
            pass
        # External commands
        else:
            add_import('subprocess')
            list_of_args, comment = str_to_array(stripped_line)
            python_script += '\t' * currIndent + f"subprocess.run({list_of_args}) {comment}\n"


    # Return the final string with shebang and imports
    shebang = "#!/usr/bin/env python3 -u\n"
    imports_string = ''
    if imports:
        imports_string = '\nimport ' + ', '.join(imports)
        imports_string.rstrip(', ')
        imports_string += '\n'

    if not use_flatten_helper:
        flatten_nested_array_str = ""

    return shebang + imports_string + flatten_nested_array_str + python_script

shell_script = sys.argv[1]
with open(shell_script, 'r') as f:
    python_script = shell_to_python(f.read())
sys.stdout.write(python_script)
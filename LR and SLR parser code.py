
This code accepts grammar as a .txt file, prints the states in its DFA in png format, the state transitions and generates the DFA as output. It also prints the LR(0) and SLR(1) parsing tables and whether the grammar is LR(0)/SLR(1) or not.
"""

!pip install termtables

import termtables as tt
import graphviz

# Adds a dot after "->" in a production rule string.
def append_dot(a):
    if "ε" in a:
        return a  # Epsilon productions don't need a dot inside
    return a.replace("->", "->.")

# Computes the closure of an item set for a given grammar, handling epsilon.
def closure(a, prod):
    temp = [a]
    for it in temp:
        if '.' not in it:
            continue  # Skip items that don't have a dot
        pos = it.index(".")
        if pos != len(it) - 1:
            jj = it[pos + 1]
            if jj.isupper():  # Check if non-terminal
                for k in prod:
                    if k.startswith(jj + "->") and append_dot(k) not in temp:
                        if k.endswith("->ε") or k.endswith("->.ε"):
                            temp.append(k)  # Directly add epsilon production
                        else:
                            temp.append(append_dot(k))
    return temp

# Swaps the dot's position in an item to the next position.
def swap(new, pos):
    new = list(new)
    if pos != len(new) - 1:
        new[pos], new[pos + 1] = new[pos + 1], new[pos]
        return "".join(new)
    return "".join(new)

# Extracts terminal symbols from the grammar.
def get_terminals(gram):
    terms = set()
    for p in gram:
        x1 = p.split('->')
        for t in x1[1].strip():
            if not t.isupper() and t != '.' and t != '' and t != 'ε':
                terms.add(t)
    terms.add('$')
    return terms

# Extracts non-terminal symbols from the grammar.
def get_non_terminals(gram):
    non_terms = set()
    for p in gram:
        non_terms.add(p.split('->')[0])
    return non_terms

# Calculates the goto set for an item and a symbol.
def goto1(x1, prod):
    if '.' not in x1:
        return []  # Return an empty list if the dot is not found to avoid errors
    pos = x1.index(".")
    if pos != len(x1) - 1:
        kk = swap(x1, pos)
        return closure(kk, prod)
    return []

# Main code to execute LR(0) related functions
if __name__ == '__main__':
    grammar_file = input("Enter the grammar file path (e.g., 'grammar.txt'): ")
    prod = []
    set_of_items = []
    c = []

    with open(grammar_file, 'r') as fp:
        for line in fp.readlines():
            prod.append(line.strip())

    start_symbol = prod[0].split('->')[0]
    augmented_start = f"X->{start_symbol}"
    prod.insert(0, append_dot(augmented_start))
    print("---------------------------------------------------------------")
    print("Augmented Grammar")
    print(prod)

    prod_num = {prod[i]: i for i in range(1, len(prod))}

    j = closure(append_dot(augmented_start), prod)
    set_of_items.append(j)

    state_numbers = {}
    dfa_prod = {}
    items = 0

    while set_of_items:
        jk = set_of_items.pop(0)
        c.append(jk)
        state_numbers[str(jk)] = items
        items += 1

        symbols = sorted(get_terminals(prod).union(get_non_terminals(prod)), key=lambda x: (x != 'S', x))
        for sym in symbols:
            new_items = set()
            for item in jk:
                if '.' in item:
                    pos = item.index('.')
                    if pos + 1 < len(item) and item[pos + 1] == sym:
                        moved_item = swap(item, pos)
                        new_items.update(closure(moved_item, prod))

            if new_items:
                new_items = list(new_items)
                if new_items not in c and new_items not in set_of_items:
                    set_of_items.append(new_items)
                dfa_prod[f"{state_numbers[str(jk)]} {sym}"] = new_items

    print("---------------------------------------------------------------")
    print("Total States: ", len(c))
    for i, items in enumerate(c):
        print(f"State {i}:")
        for item in items:
            print(f"  {item}")
        print("---------------------------------------------------------------")

    print("---------------------------------------------------------------")
    print("Flow of the States (Transitions):")
    for key, value in dfa_prod.items():
        current_state, transition = key.split()
        next_state = state_numbers.get(str(value), None)
        if next_state is not None:
            print(f"From State {current_state} on symbol {transition} -> Go to State {next_state}")
    print("---------------------------------------------------------------")

# Generate LR(0) Parsing Table
table = []
term = sorted(list(get_terminals(prod)))
non_term = sorted(list(get_non_terminals(prod) - {'X'}))
header = [''] + term + non_term
table.append(header)

table_dic = {}

for i in range(len(c)):
    data = [''] * (len(term) + len(non_term))
    samp = {}

    # Action
    for item in c[i]:
        if '.' in item and item.index('.') == len(item) - 1:  # If dot is at the end
            # This indicates a reduce move
            production = item.replace('.', '')
            if production == "X->S":  # Check for Accept state
                data[term.index('$')] = 'Accept'
                samp['$'] = 'Accept'
            elif production in prod_num:
                reduce_index = prod_num[production]
                for t in term:
                    data[term.index(t)] = f'r{reduce_index}'  # Add reduce move
                    samp[t] = f'r{reduce_index}'

    for j in dfa_prod:
        current_state, symbol = j.split()
        if int(current_state) == i:
            if symbol in term:
                data[term.index(symbol)] = 'S' + str(state_numbers.get(str(dfa_prod[j]), ''))
                samp[symbol] = 'S' + str(state_numbers.get(str(dfa_prod[j]), ''))

    # Goto
    for j in dfa_prod:
        current_state, symbol = j.split()
        if int(current_state) == i and symbol in non_term:
            data[len(term) + non_term.index(symbol)] = str(state_numbers.get(str(dfa_prod[j]), ''))
            samp[symbol] = str(state_numbers.get(str(dfa_prod[j]), ''))

    table_dic[i] = samp
    table.append([i] + data)

# Print LR(0) parsing table using termtables
final_table = tt.to_string(data=table, style=tt.styles.ascii_thin_double, padding=(0, 1))
print("\n LR(0) Parsing Table:")
print(final_table)

# Printing DFA
def visualize_dfa(dfa_prod, state_numbers):
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='LR', size='8,5')
    dot.attr('node', shape='circle')

    for key, value in dfa_prod.items():
        current_state, transition = key.split()
        next_state = state_numbers.get(str(value), None)
        if next_state is not None:
            dot.edge(f'S{current_state}', f'S{next_state}', label=transition)

    dot.render('dfa', view=True, cleanup=True)
    print("DFA has been generated and saved as 'dfa.png'.")

visualize_dfa(dfa_prod, state_numbers)

# Function to check if the grammar is LR(0) and identify conflicts
def check_lr0_grammar(c, term):
    lr0_conflict = False
    for i, state in enumerate(c):
        shift_reduce_conflict = False
        reduce_reduce_conflict = False

        actions = []
        for item in state:
            if '.' in item and item.index('.') == len(item) - 1:  # If dot is at the end (reduce)
                actions.append('reduce')
            else:
                actions.append('shift')

        # Check for conflicts
        if actions.count('reduce') > 1:
            reduce_reduce_conflict = True
        if 'shift' in actions and 'reduce' in actions:
            shift_reduce_conflict = True

        # Print conflicts if any
        if reduce_reduce_conflict:
            print(f"Conflict in State {i}: Reduce-Reduce Conflict")
            lr0_conflict = True
        if shift_reduce_conflict:
            print(f"Conflict in State {i}: Shift-Reduce Conflict")
            lr0_conflict = True

    if not lr0_conflict:
        print("The grammar is LR(0).")
    else:
        print("The grammar is NOT LR(0) due to conflicts.")

# Function call
check_lr0_grammar(c, term)

# Function to compute FIRST sets
def compute_first_sets(prod):
    first_sets = {nt: set() for nt in get_non_terminals(prod)}
    change = True

    while change:
        change = False
        for rule in prod:
            head, body = rule.split('->')
            body = body.strip()
            if body == 'ε':
                if 'ε' not in first_sets[head]:
                    first_sets[head].add('ε')
                    change = True
            else:
                for symbol in body:
                    if symbol.isupper():  # Non-terminal
                        original_length = len(first_sets[head])
                        first_sets[head].update(first_sets[symbol] - {'ε'})
                        if 'ε' in first_sets[symbol]:
                            continue
                        else:
                            break
                    else:  # Terminal
                        if symbol not in first_sets[head]:
                            first_sets[head].add(symbol)
                            change = True
                        break
                else:
                    if 'ε' not in first_sets[head]:
                        first_sets[head].add('ε')
                        change = True

    return first_sets

# Function to compute FOLLOW sets
def compute_follow_sets(prod, start_symbol):
    follow_sets = {nt: set() for nt in get_non_terminals(prod)}
    follow_sets[start_symbol].add('$')  # Start symbol always has '$'

    first_sets = compute_first_sets(prod)
    change = True

    while change:
        change = False
        for rule in prod:
            head, body = rule.split('->')
            body = body.strip()

            for i, symbol in enumerate(body):
                if symbol.isupper():  # If it's a non-terminal
                    if i + 1 < len(body):
                        next_symbol = body[i + 1]
                        if next_symbol.isupper():
                            original_length = len(follow_sets[symbol])
                            follow_sets[symbol].update(first_sets[next_symbol] - {'ε'})
                            if 'ε' in first_sets[next_symbol]:
                                follow_sets[symbol].update(follow_sets[head])
                            if len(follow_sets[symbol]) > original_length:
                                change = True
                        else:
                            if next_symbol not in follow_sets[symbol]:
                                follow_sets[symbol].add(next_symbol)
                                change = True
                    else:
                        original_length = len(follow_sets[symbol])
                        follow_sets[symbol].update(follow_sets[head])
                        if len(follow_sets[symbol]) > original_length:
                            change = True

    return follow_sets

# Function to generate and print the SLR(1) parsing table and identify conflicts
def generate_slr1_table(c, term, non_term, prod, prod_num, follow_sets):
    table = []
    header = [''] + term + non_term
    table.append(header)
    table_dic = {}  # Dictionary to store the parsing table
    slr1_conflict = False

    for i in range(len(c)):
        data = [''] * (len(term) + len(non_term))
        samp = {}

        # Action
        for item in c[i]:
            if '.' in item and item.index('.') == len(item) - 1:  # If dot is at the end (reduce)
                production = item.replace('.', '')
                if production == "X->S":  # Check for Accept state
                    data[term.index('$')] = 'Accept'
                    samp['$'] = 'Accept'
                elif production in prod_num:
                    reduce_index = prod_num[production]
                    for t in follow_sets[production.split('->')[0]]:  # Use FOLLOW set for the reduce
                        if data[term.index(t)] != '' and data[term.index(t)] != f'r{reduce_index}':
                            print(f"Conflict in State {i} on symbol '{t}': Reduce-Reduce or Shift-Reduce Conflict")
                            slr1_conflict = True
                        data[term.index(t)] = f'r{reduce_index}'  # Add reduce move
                        samp[t] = f'r{reduce_index}'

        for j in dfa_prod:
            current_state, symbol = j.split()
            if int(current_state) == i:
                if symbol in term:
                    if data[term.index(symbol)] != '' and data[term.index(symbol)] != 'S' + str(state_numbers.get(str(dfa_prod[j]), '')):
                        print(f"\nConflict in State {i} on symbol '{symbol}'")
                        slr1_conflict = True
                    data[term.index(symbol)] = 'S' + str(state_numbers.get(str(dfa_prod[j]), ''))
                    samp[symbol] = 'S' + str(state_numbers.get(str(dfa_prod[j]), ''))

        # Goto
        for j in dfa_prod:
            current_state, symbol = j.split()
            if int(current_state) == i and symbol in non_term:
                data[len(term) + non_term.index(symbol)] = str(state_numbers.get(str(dfa_prod[j]), ''))
                samp[symbol] = str(state_numbers.get(str(dfa_prod[j]), ''))

        table_dic[i] = samp
        table.append([i] + data)

    # Print the SLR(1) table using termtables
    final_table = tt.to_string(data=table, style=tt.styles.ascii_thin_double, padding=(0, 1))
    print("\nSLR(1) Parsing Table:")
    print(final_table)

    if not slr1_conflict:
        print("The grammar is SLR(1).")
    else:
        print("The grammar is NOT SLR(1) due to conflicts.")

# Main code to compute FOLLOW sets and generate the SLR(1) table
start_symbol = prod[1].split('->')[0]  # Use the first non-augmented production's LHS as the start symbol
follow_sets = compute_follow_sets(prod, start_symbol)
print("FOLLOW sets:")
for nt, follows in follow_sets.items():
    if nt != 'X':  # Skip printing the FOLLOW set for the augmented non-terminal 'X'
        print(f"{nt}: {follows}")

# Call the function to generate and print the SLR(1) table
generate_slr1_table(c, term, non_term, prod, prod_num, follow_sets)

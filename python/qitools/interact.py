"""Small set of tools to interact with the user

"""

#TODO: color !

def ask_choice(choices, input_text):
    """Ask the user to choose from a list of choices

    """
    print "::", input_text
    for i, choice in enumerate(choices):
        print "  ", (i+1), choice
    keep_asking = True
    res = None
    while keep_asking:
        answer = raw_input("> ")
        if not answer:
            return choices[0]
        try:
            index = int(answer)
        except ValueError:
            print "Please enter number"
            continue
        if index not in range(1, len(choices)+1):
            print "%i is out of range" % index
            continue
        res = choices[index-1]
        keep_asking = False

    return res

def ask_yes_no(question):
    """Ask the user to answer by yes or no"""
    print "::", question, "(y/n)?"
    anwer = raw_input("> ")
    return anwer == "y"

" Generate source/generated.rst "

def main():
    with open("source/generated.rst", "w") as fp:
        fp.write("""\
Generated section
=================

""")

if __name__ == "__main__":
    main()

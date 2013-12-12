
def theme():
    # qibuild theme:

    return [
        [ "^\* (\(\s*[0-9]+/[0-9]+\)) (Configuring|Building) (.*)$", "yellow,magenta,green", "normal,normal,bold" ],
        [ "^\* (\(\s*[0-9]+/[0-9]+\)) (Deploying) project ([^ ]*) to (.*)$", "yellow,magenta,green,green", "normal,normal,bold,bold" ]
    ]


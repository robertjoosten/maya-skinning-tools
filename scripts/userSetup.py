from maya import cmds


def main():
    from skinning import install
    install.execute()


cmds.evalDeferred(main)

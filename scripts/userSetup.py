from maya import cmds


def main():
    from skinning_tools import install
    install.execute()


cmds.evalDeferred(main)

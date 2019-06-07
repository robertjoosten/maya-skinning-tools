__all__ = [
    "BlockSignals"
]


class BlockSignals(object):
    """
    The block signals context is used to block the signals of the parsed
    widgets while the code is being executed.

    with BlockSignals(*widgets):
        # code
    """

    def __init__(self, *args):
        self.widgets = args

    def __enter__(self):
        for widget in self.widgets:
            widget.blockSignals(True)

    def __exit__(self, *exc_info):
        for widget in self.widgets:
            widget.blockSignals(False)

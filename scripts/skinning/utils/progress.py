import logging
from maya import mel
from maya import cmds


__all__ = [
    "Progress"
]

log = logging.getLogger(__name__)


class Progress(object):
    """
    The progress context is used to indicate to the user that progress is
    being made on task. The context needs to be used in a "with" statement.
    In this with statement the message and number if iterations is defined.
    After this the class method next can be called to increment the value by
    one.

    with Progress(1000, "iterator") as progress:
        progress.next()
    """
    def __init__(self, total, message=None):
        # set numeration variables
        self.value = 0
        self.total = total
        self.message = message

        # get progress bar
        self.path = None
        self.batch = cmds.about(batch=True)

        if not self.batch:
            self.path = mel.eval("$tmp = $gMainProgressBar")
            cmds.progressBar(
                self.path,
                edit=True,
                isInterruptable=False,
                status=self.message,
                minValue=0,
                maxValue=total
            )

    def __enter__(self):
        if not self.batch:
            cmds.progressBar(self.path, edit=True, status=self.message, beginProgress=True)

        return self

    def __exit__(self, *exc_info):
        if not self.batch:
            cmds.progressBar(self.path, edit=True, endProgress=True)

    # ------------------------------------------------------------------------

    def next(self):
        """
        Increment the value and update the progress bar or log progress status
        depending on the batch state of Maya.
        """
        self.value += 1

        if not self.batch:
            cmds.progressBar(self.path, edit=True, status=self.message, step=1)
        else:
            log.info("{} {}/{}".format(self.message, self.value, self.total))



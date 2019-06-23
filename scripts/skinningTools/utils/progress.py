from maya import cmds, mel
from .singleton import Singleton


__all__ = [
    "Progress"
]


class Progress(object):
    """
    The progress context is used to indicate to the user that progress is
    being made on task. The context needs to be used in a "with" statement.
    In this with statement the message and number if iterations is defined.
    After this the class method next can be called to increment the value by
    one.

    with Progress(1000, "iterator"):
        # code
    """
    __metaclass__ = Singleton

    def __init__(self, total, message=None):
        # set numeration variables
        self._value = 0
        self._total = total
        self._message = message

        # get progress bar
        self._bar = None
        self._batch = cmds.about(batch=True)

        if not self._batch:
            self._bar = mel.eval("$tmp = $gMainProgressBar")
            cmds.progressBar(
                self._bar,
                edit=True,
                isInterruptable=False,
                status=self.message,
                minValue=0,
                maxValue=total
            )

    def __enter__(self):
        if not self._batch:
            cmds.progressBar(
                self._bar,
                edit=True,
                status=self.message,
                beginProgress=True
            )

    def __exit__(self, *exc_info):
        if not self._batch:
            cmds.progressBar(
                self._bar,
                edit=True,
                endProgress=True
            )

    # ------------------------------------------------------------------------

    @classmethod
    def next(cls):
        progress = cls()
        progress.value += 1

    # ------------------------------------------------------------------------

    @property
    def message(self):
        """
        :return: Message
        :rtype: str
        """
        return self._message

    # ------------------------------------------------------------------------

    @property
    def value(self):
        """
        :param int value:
        :return: Progress value
        :rtype: int
        """
        return self._value

    @value.setter
    def value(self, value):
        # set value
        self._value = value

        # update ui
        if not self._batch:
            cmds.progressBar(
                self._bar,
                edit=True,
                status=self.message,
                step=1
            )

        # print progress when running in batch
        else:
            print "{} {}/{}".format(self.message, self.value, self.total)

    # ------------------------------------------------------------------------

    @property
    def total(self):
        """
        :return: Progress total
        :rtype: int
        """
        return self._total

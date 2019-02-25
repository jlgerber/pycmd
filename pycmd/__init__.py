rom abc import ABCMeta
from abc import abstractmethod
import logging

class Command(object):
    """
    Abstract base class for commands.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def do(self):
        pass

    @abstractmethod
    def undo(self):
        pass

class Executor(object):
    def __init__(self, logger=logging.getLogger(__name__)):
        self._stack = []
        self._exceptions = []
        self.logger = logger

    def exec_cmd(self, cmd):
        """
        execute command. If successful, add
        it to the stack. Otherwise, unwind the
        stack

        :param cmd: Command to execute
        :param type: Command subclass

        :return: success or failure
        :return type: bool
        """
        try:
            self.logger.debug("executor.exec_cmd calling command: {}".format(cmd))
            cmd.do()
            return True
        except Exception:
            try:
                self.logger.error("exeutor.exec_cmd() failed. Unwinding stack.")
                self.logger.debug("calling cmd.undo()")
                cmd.undo()
            except Exception as err:
                self.logger.error("executor.exec_cmd() undo failed with '{}'".format(err))
                self._exceptions.append(err)
            while self._stack.len():
                cmd = self._stack.pop()
                self.debug("calling cmd.undo on '{}'".format(cmd))
                try:
                    cmd.undo()
                except Exception as err:
                    self.logger.error("executor.exec_cmd() unwinding stack failure: '{}'".format(err))
                    self._exceptions.append(err)
            return False

    @property
    def exceptions(self):
        return self._exceptions
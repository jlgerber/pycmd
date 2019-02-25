from abc import ABCMeta
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
        self._cmd_stack = []
        self._exceptions = []
        self.logger = logger
        self.failed = False

    def add_cmd(self, cmd):
        """
        Add a command
        """
        assert isinstance(cmd, Command), "cmd must be instance of pycmd.Command"
        self._cmd_stack.append(cmd)

    def execute(self):
        """
        Execute commands which have previously been added
        """
        if len(self._cmd_stack) == 0:
            raise RuntimeError("Command Stack is Empty")

        for cmd in self._cmd_stack:
            if not self._exec_cmd(cmd):
                return False
        return True

    def _exec_cmd(self, cmd):
        try:
            self.logger.debug("executor.exec_cmd calling command: {}".format(cmd))
            cmd.do()
            self._stack.append(cmd)
            return True
        except Exception:
            self.failed = True
            try:
                self.logger.error("exeutor.exec_cmd() failed. Unwinding stack.")
                self.logger.debug("calling cmd.undo()")
                cmd.undo()
            except Exception as err:
                self.logger.error("executor.exec_cmd() undo failed with '{}'".format(err))
                self._exceptions.append(err)
            self.logger.debug("stack len {}".format(len(self._stack)))
            while len(self._stack) > 0:
                cmd = self._stack.pop()
                self.logger.debug("calling cmd.undo on '{}'".format(cmd))
                try:
                    cmd.undo()
                except Exception as err:
                    self.logger.error("executor.exec_cmd() unwinding stack failure: '{}'".format(err))
                    self._exceptions.append(err)
            return False

    def exec_cmd(self, cmd):
        """
        Execute command. If successful, add
        it to the stack. Otherwise, unwind the
        stack

        :param cmd: Command to execute
        :param type: Command subclass

        :return: success or failure
        :return type: bool
        """
        assert len(self._cmd_stack) == 0, "cannot mix exe_cmd and add_cmd/exe"

        if self.failed:
            self.logger.error("executor.exec_cmd short circuting")
            return False
        return self._exec_cmd(cmd)

    @property
    def exceptions(self):
        return self._exceptions
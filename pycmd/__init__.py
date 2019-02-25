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
        self._failed = None

    @property
    def failed(self):
        if self._failed is None:
            return False
        return True

    @property
    def failed_cmd(self):
        return self._failed

    @property
    def exceptions(self):
        return self._exceptions

    def add_cmd(self, cmd):
        """
        Add a command to the executor command stack, in preparation for execution.

        :param cmd: The command to be added
        :param type: Command subclass

        :raises: AssertionError if cmd is not a subclass of Command

        :returns: None
        """
        assert isinstance(cmd, Command), "cmd must be instance of pycmd.Command"
        self._cmd_stack.append(cmd)

    def execute(self):
        """
        Execute commands which have previously been added via `add_cmd`.

        :raises: RuntimeError if the command stack is empty
        :return: Wether execution of stack succeeded or failed
        :return type: bool
        """
        if len(self._cmd_stack) == 0:
            raise RuntimeError("Command Stack is Empty")

        for cmd in self._cmd_stack:
            if not self._exec_cmd(cmd):
                self.logger.error("executor.execute() failed on {}".format(self.failed_cmd))
                return False
        return True

    def exec_cmd(self, cmd):
        """
        As an alternative to using `add_cmd` and `execute`, you can execute commands one at a time,
        pushing them onto the stack if successful, and unwinding the stack if unsuccessful.
        This alternative may be used, for example. if each command is expensive to initialize.

        Once an exec_cmd call fails, subsequent calls to exec_cmd will short curcuit and
        return False without any additional action. Effectively, the executor is a one shot affair.

        :param cmd: Command to execute
        :param type: Command subclass

        :return: success or failure
        :return type: bool
        """
        assert len(self._cmd_stack) == 0, "cannot mix exe_cmd and add_cmd/exe"

        if self.failed:
            self.logger.error("executor.exec_cmd short circuting. Failed on {}".format(self.failed_cmd))
            return False

        return self._exec_cmd(cmd)

    def _exec_cmd(self, cmd):
        try:
            self.logger.debug("executor.exec_cmd calling command: {}".format(cmd))
            cmd.do()
            self._stack.append(cmd)
            return True
        except Exception:
            self._failed = str(cmd)
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

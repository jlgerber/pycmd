import unittest
from context import pycmd

class State(object):
    def __init__(self):
        self.cmda_exe=None
        self.cmdb_exe=None

class CmdA(pycmd.Command):
    def __init__(self, state):
        self.state = state

    def do(self):
        self.state.cmda_exe="cmda success"

    def undo(self):
        self.state.cmda_exe="cmda undone"


class CmdB(pycmd.Command):
    def __init__(self, state):
        self.state = state

    def do(self):
        self.state.cmdb_exe="cmdb success"

    def undo(self):
        self.state.cmdb_exe="cmdb undone"


class CmdAFail(pycmd.Command):
    def __init__(self, state):
        self.state = state

    def do(self):
        raise RuntimeError("cmda failed")

    def undo(self):
        self.state.cmda_exe="cmda undone"


class CmdBFail(pycmd.Command):
    def __init__(self, state):
        self.state = state

    def do(self):
        raise RuntimeError("cmdb failed")

    def undo(self):
        self.state.cmdb_exe="cmdb undone"


class ExeCmdTest(unittest.TestCase):
    def test_cmd_execute_success(self):
        state = State()
        cmda = CmdA(state)
        cmdb = CmdB(state)
        executor = pycmd.Executor()

        result = executor.exec_cmd(cmda)
        self.assertTrue(result)
        result = executor.exec_cmd(cmdb)
        self.assertTrue(result)

        self.assertEqual(state.cmda_exe, "cmda success")
        self.assertEqual(state.cmdb_exe, "cmdb success")

    def test_cmd_execute_fail_b(self):
        state = State()
        cmda = CmdA(state)
        cmdb = CmdBFail(state)
        executor = pycmd.Executor()

        result = executor.exec_cmd(cmda)
        self.assertTrue(result)
        result = executor.exec_cmd(cmdb)
        self.assertFalse(result)

        self.assertEqual(state.cmda_exe, "cmda undone")
        self.assertEqual(state.cmdb_exe, "cmdb undone")
        self.assertTrue(executor.failed.startswith("<test_cmd.CmdBFail"))

    def test_cmd_execute_fail_a(self):
        state = State()
        cmda = CmdAFail(state)
        cmdb = CmdB(state)
        executor = pycmd.Executor()

        result = executor.exec_cmd(cmda)
        self.assertFalse(result)

        result = executor.exec_cmd(cmdb)
        self.assertFalse(result)

        self.assertEqual(state.cmda_exe, "cmda undone")
        self.assertEqual(state.cmdb_exe, None)
        self.assertTrue(executor.failed.startswith("<test_cmd.CmdAFail"))


class AddCmdTest(unittest.TestCase):
    def test_cmd_execute_success(self):
        state = State()
        cmda = CmdA(state)
        cmdb = CmdB(state)
        executor = pycmd.Executor()

        executor.add_cmd(cmda)
        executor.add_cmd(cmdb)
        executor.execute()

        self.assertEqual(state.cmda_exe, "cmda success")
        self.assertEqual(state.cmdb_exe, "cmdb success")

    def test_cmd_execute_fail_b(self):
        state = State()
        cmda = CmdA(state)
        cmdb = CmdBFail(state)
        executor = pycmd.Executor()

        executor.add_cmd(cmda)
        executor.add_cmd(cmdb)
        executor.execute()

        self.assertEqual(state.cmda_exe, "cmda undone")
        self.assertEqual(state.cmdb_exe, "cmdb undone")
        self.assertTrue(executor.failed.startswith("<test_cmd.CmdBFail"))

    def test_cmd_execute_fail_a(self):
        state = State()
        cmda = CmdAFail(state)
        cmdb = CmdB(state)
        executor = pycmd.Executor()

        executor.add_cmd(cmda)
        executor.add_cmd(cmdb)
        executor.execute()

        self.assertEqual(state.cmda_exe, "cmda undone")
        self.assertEqual(state.cmdb_exe, None)
        self.assertTrue(executor.failed.startswith("<test_cmd.CmdAFail"))

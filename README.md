# pycmd
Simple command pattern implementation in python.

## Synopsys

The `pycmd` module consists of two classes:
- **Command**: The base class for commands, providing abstract `do` and `undo` methods
- **Executor**: The command executor, providing a means of `do`ing a stack of commands, and `undo`ing said stack if a failure occurs.

## Usage

### Define Commands
To define a new command, inherit from Command and override the `do` and `undo` methods. All exception handling is the responsibility of the Executor, so do not catch exceptions in the derived command. If the command is not undoable, implement `undo` as pass.

### Choice 1 - Stack and Execute
There are two ways to use the Executor. The first way, is to first instantiate all commands, adding each to the executor via `add_cmd`, and then execute the stack of commands via `execute`.

#### Example
```python
executor = Executor()
executor.add_cmd(cmd_a())
executor.add_cmd(cmd_b())
executor.add_cmd(cmd_c())
executor.execute()
if executor.failed:
    print "Failure", executor.failed
```

### Choice 2 - Immediate Cmd execution
You can also execute commands as you go. You might want to use this if instantiating each command is expensive.

```python
executor = Executor()
if not executor.exec_command(cmd_a()):
    return
...
if not executor.exec_command(cmd_b()):
    return
```
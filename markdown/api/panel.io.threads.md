# panel.io.threads module

class panel.io.threads.StoppableThread(io_loop, owns_loop: bool = False, **kwargs)
Bases: `Thread`

Thread class with a stop() method.

Methods

|  |  |
|----|----|
| [run](#panel.io.threads.StoppableThread.run)() | Method representing the thread's activity. |

|          |     |
|----------|-----|
| **stop** |     |

run() → None
Method representing the thread’s activity.

You may override this method in a subclass. The standard run() method
invokes the callable object passed to the object’s constructor as the
target argument, if any, with sequential and keyword arguments taken
from the args and kwargs arguments, respectively.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page

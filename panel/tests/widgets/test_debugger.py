"""This module contains tests of the Debugger"""
import logging

import panel as pn


def test_debugger_constructor():
    debugger = pn.widgets.Debugger()

    assert repr(debugger).startswith("Debugger(")


    debugger = pn.widgets.Debugger(only_last=False)
    assert repr(debugger).startswith("Debugger(")

    debugger = pn.widgets.Debugger(level=20)
    assert repr(debugger).startswith("Debugger(")


def test_debugger_logging():
    logger = logging.getLogger('panel.callbacks')
    debugger = pn.widgets.Debugger()

    logger.info('test')

    assert debugger.terminal.output == ''
    assert debugger.title == ''

    logger.error('error test')

    assert 'error test' in debugger.terminal.output
    assert 'errors: </span>1' in debugger.title

    debugger.terminal._clears+=1
    assert debugger.title == ''
    #TODO: test if debugger.terminal.output is cleared by JS callback.


def test_debugger_logging_info():
    logger = logging.getLogger('panel.callbacks')
    debugger = pn.widgets.Debugger(level=logging.DEBUG)
    msg = 'debugger test message'
    logger.info(msg)

    assert msg in debugger.terminal.output
    assert debugger.title == 'i: 1'

    msg = 'debugger test warning'
    logger.warning(msg)

    assert msg in debugger.terminal.output
    assert 'w: </span>1' in debugger.title

"""
The Debugger Widget is an uneditable Card that gives you feedback on errors 
thrown by your Panel callbacks.
"""
import param

#relative imports
from .terminal import Terminal
from .button import Button
from ..layout.card import Card
from ..layout import Row
from ..pane.markup import Str

from .indicators import BooleanStatus
import logging
from ..io.state import state



class TermFormatter(logging.Formatter):
    
    
    def __init__(self, *args, only_last=True, **kwargs):
        """
        Standard logging.Formatter with the default option of prompting
        only the last stack. Does not cache exc_text.

        Parameters
        ----------
        only_last : BOOLEAN, optional
            Whether the full stack trace or only the last file should be shown. 
            The default is True.

        Returns
        -------
        None.

        """
        
        super().__init__(*args, **kwargs)    
        self.only_last = only_last
    
    def format(self, record):
        
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self.formatMessage(record)
        exc_text = None
        if record.exc_info:
            exc_text = super().formatException(record.exc_info)
            last = exc_text.rfind('File')
            if last >0 and self.only_last:
                exc_text = exc_text[last:]
        if exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)
        return s
    
    
class CheckFilter(logging.Filter):
    
    
    def add_debugger(self, debugger):
        """
        

        Parameters
        ----------
        widg : panel.widgets.Debugger
            The widget displaying the logs.

        Returns
        -------
        None.

        """
        self.debugger = debugger
    
    def filter(self,record):
        """
        Will filter out messages coming from a different bokeh document than
        the document where the debugger is embedded.

        """
        
        if state.curdoc:
            session_id = state.curdoc.session_context.id
        else:
            self.debugger.number_of_errors += 1
            return True
        
        if hasattr(self,'debugger'):
            self.debugger.number_of_errors += 1
            widget_session_ids = set(m.document.session_context.id 
                              for m in sum(self.debugger._models.values(),tuple()))
            if session_id not in widget_session_ids:
                return False
        
        return True
    
    
class Debugger(Card):
    
    number_of_errors = param.Integer(doc="Number of logged messages since last acknowledged", 
                                      bounds=(0, None))
    
    _rename = Card._rename.copy()
    _rename.update({'number_of_errors': None})
    
    def __init__(self, *args,only_last=True,level=logging.ERROR, **kwargs):
        super().__init__( *args, **kwargs)
        #change default css
        self.button_css_classes = ['debugger-card-button']
        self.css_classes = ['debugger-card']
        self.header_css_classes = ['debugger-card-header']
        self.title_css_classes = ['debugger-card-title']
        
        
        
        terminal = Terminal(height = self.height - 50 if self.height else None,
                            sizing_mode='stretch_width')
        stream_handler = logging.StreamHandler(terminal)
        stream_handler.terminator = "  \n"
        
        formatter = TermFormatter("%(asctime)s [%(levelname)s]: %(message)s",
                          only_last=True)

        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        curr_filter = CheckFilter()
        
        curr_filter.add_debugger(self)
        
        stream_handler.addFilter(curr_filter)
        
        logger=  logging.getLogger('panel.callbacks')
        logger.addHandler(stream_handler)
        
        #header
        self.param.watch(self.update_log_counts,'number_of_errors')
        
        #body
        self.ackn_btn = Button(name='Acknowledge errors')
        self.ackn_btn.on_click(self.acknowledge_errors)
        self.terminal = terminal
        self.append(terminal)
        self.append(self.ackn_btn)
        
        #make it an uneditable card
        self.param['objects'].constant = True
        
        self.collapsed = True
                
    def update_log_counts(self, event):
        if self.number_of_errors:
            self.title = f'<p><span style="color:rgb(190,0,0);">errors: </span> {self.number_of_errors}</p>'
        else:
            self.title = ''
        
        
    def acknowledge_errors(self,event):
        self.number_of_errors = 0
        self.terminal.clear()
        
    
        
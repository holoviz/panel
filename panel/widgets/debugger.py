"""
The Debugger Widget is an uneditable Card that gives you feedback on errors 
thrown by your Panel callbacks.
"""
import param
import logging

#relative imports
from .terminal import Terminal
from ..layout.card import Card
from ..reactive import ReactiveHTML
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
    
    def _update_debugger(self, record):
        if not hasattr(self, 'debugger'):
            return
        if record.levelno >= 40:
            self.debugger._number_of_errors += 1
        elif 40 > record.levelno >= 30:
            self.debugger._number_of_warnings += 1
        elif record.levelno < 30:
            self.debugger._number_of_infos += 1
            
    
    def filter(self,record):
        """
        Will filter out messages coming from a different bokeh document than
        the document where the debugger is embedded in server mode.
        Returns True if no debugger was added.

        """        
        if hasattr(self,'debugger'):#
            if state.curdoc:
                session_id = state.curdoc.session_context.id                
                widget_session_ids = set(m.document.session_context.id 
                                  for m in sum(self.debugger._models.values(),
                                               tuple()) if m.document.session_context)
                if session_id not in widget_session_ids:
                    return False                        
            self._update_debugger(record)
            
        
        return True
    
class TermButton(ReactiveHTML):
    clicks = param.Integer(default=0)
    title = param.String(doc="Text shown on button", default='Clear')
    #Note: using name instead of title will thrown an error.
    _template = """<button id="clear" onclick='${_input_change}' 
                           style="width: ${model.width}px;height: 25px;background-color: black;color: white">Clear</button>"""
    
    def _input_change(self, event):
        self.clicks += 1


class Debugger(Card):
    """
    A uneditable Card layout holding a terminal printing out logs from your 
    callbacks. By default, it will only print exceptions. If you want to add
    your own log, use the `panel.callbacks` logger within your callbacks:
    `logger = logging.getLogger('panel.callbacks')`
    """
    
    _number_of_errors = param.Integer(doc="Number of logged errors since last acknowledged", 
                                      bounds=(0, None),
                                      precedence=-1)
    _number_of_warnings = param.Integer(doc="Number of logged warnings since last acknowledged", 
                                      bounds=(0, None),
                                      precedence=-1)
    _number_of_infos = param.Integer(doc="Number of logged informations since last acknowledged", 
                                      bounds=(0, None),
                                      precedence=-1)
    only_last = param.Boolean(doc="Whether only the last stack is printed or the full",
                              default=True)
    level = param.Integer(doc=("Logging level to print in the debugger terminal. "
                               "Unless you explicitely use the `panel.callbacks` "
                               "logger within your callbacks, "
                               "Only exceptions (errors) are caught for the moment."),
                          default = logging.ERROR)
    _rename = Card._rename.copy()
    _rename.update({'_number_of_errors': None,
                    '_number_of_warning': None,
                    '_number_of_infos': None,
                    'only_last': None,
                    'level': None})
    
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        #change default css
        self.button_css_classes = ['debugger-card-button']
        self.css_classes = ['debugger-card']
        self.header_css_classes = ['debugger-card-header']
        self.title_css_classes = ['debugger-card-title']
        
        
        
        terminal = Terminal(min_height=200,
                            min_width=400,
                            sizing_mode='stretch_width')
        stream_handler = logging.StreamHandler(terminal)
        stream_handler.terminator = "  \n"
        
        formatter = TermFormatter("%(asctime)s [%(levelname)s]: %(message)s",
                          only_last=self.only_last)

        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(self.level)
        curr_filter = CheckFilter()
        
        curr_filter.add_debugger(self)
        
        stream_handler.addFilter(curr_filter)
        
        logger=  logging.getLogger('panel.callbacks')
        logger.addHandler(stream_handler)
        
        #header
        self.param.watch(self.update_log_counts,'_number_of_errors')
        self.param.watch(self.update_log_counts,'_number_of_warnings')
        self.param.watch(self.update_log_counts,'_number_of_infos')
        
        #body
        self.ackn_btn = TermButton(width=terminal.width)#setting title directly will throw a ValueError
        #as it gets converted to a .pane.markup.Markdown object.
        self.ackn_btn.title='Acknowledge errors'
        self.ackn_btn.param.watch(self.acknowledge_errors, ['clicks'])
        self.terminal = terminal
        self.append(self.ackn_btn)
        self.append(terminal)
        
        #make it an uneditable card
        self.param['objects'].constant = True
        
        #by default it should be collapsed and small.
        self.collapsed = True
          
    
    def update_log_counts(self, event):
        title = []
        
        if self._number_of_errors:
            title.append(f'<span style="color:rgb(190,0,0);">errors: </span>{self._number_of_errors}')
        if self._number_of_warnings:
            title.append(f'<span style="color:rgb(190,160,20);">w: </span>{self._number_of_warnings}')
        if self._number_of_infos:
            title.append(f'i: {self._number_of_infos}')
            
        self.title = ', '.join(title)
        
        
    def acknowledge_errors(self,event):
        self._number_of_errors = 0
        self._number_of_warnings = 0
        self._number_of_infos = 0
        self.terminal.clear()
        
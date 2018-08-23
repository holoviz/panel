import json
import uuid
import sys
import traceback

try:
    from StringIO import StringIO
except:
    from io import StringIO

import param

__version__ = str(param.version.Version(fpath=__file__, archive_commit="$Format:%h$",
                                        reponame="pyviz_comms"))


PYVIZ_PROXY = """
if (window.PyViz === undefined) {
   if (window.HoloViews === undefined) {
     var PyViz = {comms: {}, comm_status:{}, kernels:{}, receivers: {}, plot_index: []}
   } else {
     var PyViz = window.HoloViews;
   }
   window.PyViz = PyViz;
   window.HoloViews = PyViz;  // TEMPORARY HACK TILL NEXT NPM RELEASE
}
"""


# Following JS block becomes body of the message handler callback
bokeh_msg_handler = """
var plot_id = "{plot_id}";
if (plot_id in window.PyViz.plot_index) {{
  var plot = window.PyViz.plot_index[plot_id];
}} else {{
  var plot = Bokeh.index[plot_id];
}}

if (plot_id in window.PyViz.receivers) {{
  var receiver = window.PyViz.receivers[plot_id];
}} else if (Bokeh.protocol === undefined) {{
  return;
}} else {{
  var receiver = new Bokeh.protocol.Receiver();
  window.PyViz.receivers[plot_id] = receiver;
}}

if (buffers.length > 0) {{
  receiver.consume(buffers[0].buffer)
}} else {{
  receiver.consume(msg)
}}

const comm_msg = receiver.message;
if (comm_msg != null) {{
  plot.model.document.apply_json_patch(comm_msg.content, comm_msg.buffers)
}}
"""

embed_js = """
// Ugly hack - see HoloViews #2574 for more information
if (!(document.getElementById('{plot_id}')) && !(document.getElementById('_anim_img{widget_id}'))) {{
  console.log("Creating DOM nodes dynamically for assumed nbconvert export. To generate clean HTML output set HV_DOC_HTML as an environment variable.")
  var htmlObject = document.createElement('div');
  htmlObject.innerHTML = `{html}`;
  var scriptTags = document.getElementsByTagName('script');
  var parentTag = scriptTags[scriptTags.length-1].parentNode;
  parentTag.append(htmlObject)
}}
"""

JS_CALLBACK = """
function unique_events(events) {{
  // Processes the event queue ignoring duplicate events
  // of the same type
  var unique = [];
  var unique_events = [];
  for (var i=0; i<events.length; i++) {{
    var _tmpevent = events[i];
    event = _tmpevent[0];
    data = _tmpevent[1];
    if (unique_events.indexOf(event)===-1) {{
      unique.unshift(data);
      unique_events.push(event);
      }}
  }}
  return unique;
}}

function process_events(comm_status) {{
  // Iterates over event queue and sends events via Comm
  var events = unique_events(comm_status.event_buffer);
  for (var i=0; i<events.length; i++) {{
    var data = events[i];
    var comm = window.PyViz.comms[data["comm_id"]];
    comm.send(data);
  }}
  comm_status.event_buffer = [];
}}

function on_msg(msg) {{
  // Receives acknowledgement from Python, processing event
  // and unblocking Comm if event queue empty
  msg = JSON.parse(msg.content.data);
  var comm_id = msg["comm_id"]
  var comm_status = window.PyViz.comm_status[comm_id];
  if (comm_status.event_buffer.length) {{
    process_events(comm_status);
    comm_status.blocked = true;
    comm_status.time = Date.now()+{debounce};
  }} else {{
    comm_status.blocked = false;
  }}
  comm_status.event_buffer = [];
  if ((msg.msg_type == "Ready") && msg.content) {{
    console.log("Python callback returned following output:", msg.content);
  }} else if (msg.msg_type == "Error") {{
    console.log("Python failed with the following traceback:", msg['traceback'])
  }}
}}

// Initialize Comm
comm = window.PyViz.comm_manager.get_client_comm("{plot_id}", "{comm_id}", on_msg);
if (!comm) {{
  return
}}

// Initialize event queue and timeouts for Comm
var comm_status = window.PyViz.comm_status["{comm_id}"];
if (comm_status === undefined) {{
  comm_status = {{event_buffer: [], blocked: false, time: Date.now()}}
  window.PyViz.comm_status["{comm_id}"] = comm_status
}}

// Add current event to queue and process queue if not blocked
event_name = cb_obj.event_name
data['comm_id'] = "{comm_id}";
timeout = comm_status.time + {timeout};
if ((comm_status.blocked && (Date.now() < timeout))) {{
  comm_status.event_buffer.unshift([event_name, data]);
}} else {{
  comm_status.event_buffer.unshift([event_name, data]);
  setTimeout(function() {{ process_events(comm_status); }}, {debounce});
  comm_status.blocked = true;
  comm_status.time = Date.now()+{debounce};
}}
"""


class StandardOutput(list):
    """
    Context manager to capture standard output for any code it
    is wrapping and make it available as a list, e.g.:

    >>> with StandardOutput() as stdout:
    ...   print('This gets captured')
    >>> print(stdout[0])
    This gets captured
    """

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout


class Comm(param.Parameterized):
    """
    Comm encompasses any uni- or bi-directional connection between
    a python process and a frontend allowing passing of messages
    between the two. A Comms class must implement methods
    send data and handle received message events.

    If the Comm has to be set up on the frontend a template to
    handle the creation of the comms channel along with a message
    handler to process incoming messages must be supplied.

    The template must accept three arguments:

    * id          -  A unique id to register to register the comm under.
    * msg_handler -  JS code which has the msg variable in scope and
                     performs appropriate action for the supplied message.
    * init_frame  -  The initial frame to render on the frontend.
    """

    html_template = """
    <div id="fig_{plot_id}">
      {init_frame}
    </div>
    """

    id = param.String(doc="Unique identifier of this Comm instance")

    js_template = ''

    def __init__(self, id=None, on_msg=None):
        """
        Initializes a Comms object
        """
        self._on_msg = on_msg
        self._comm = None
        super(Comm, self).__init__(id = id if id else uuid.uuid4().hex)


    def init(self, on_msg=None):
        """
        Initializes comms channel.
        """


    def send(self, data=None, buffers=[]):
        """
        Sends data to the frontend
        """


    @classmethod
    def decode(cls, msg):
        """
        Decode incoming message, e.g. by parsing json.
        """
        return msg


    @property
    def comm(self):
        if not self._comm:
            raise ValueError('Comm has not been initialized')
        return self._comm


    def _handle_msg(self, msg):
        """
        Decode received message before passing it to on_msg callback
        if it has been defined.
        """
        comm_id = None
        try:
            stdout = []
            msg = self.decode(msg)
            comm_id = msg.pop('comm_id', None)
            if self._on_msg:
                # Comm swallows standard output so we need to capture
                # it and then send it to the frontend
                with StandardOutput() as stdout:
                    self._on_msg(msg)
        except Exception as e:
            frame =traceback.extract_tb(sys.exc_info()[2])[-2]
            fname,lineno,fn,text = frame
            error_kwargs = dict(type=type(e).__name__, fn=fn, fname=fname,
                                line=lineno, error=str(e))
            error = '{fname} {fn} L{line}\n\t{type}: {error}'.format(**error_kwargs)
            if stdout:
                stdout = '\n\t'+'\n\t'.join(stdout)
                error = '\n'.join([stdout, error])
            reply = {'msg_type': "Error", 'traceback': error}
        else:
            stdout = '\n\t'+'\n\t'.join(stdout) if stdout else ''
            reply = {'msg_type': "Ready", 'content': stdout}

        # Returning the comm_id in an ACK message ensures that
        # the correct comms handle is unblocked
        if comm_id:
            reply['comm_id'] = comm_id
        self.send(json.dumps(reply))


class JupyterComm(Comm):
    """
    JupyterComm provides a Comm for the notebook which is initialized
    the first time data is pushed to the frontend.
    """

    js_template = """
    function msg_handler(msg) {{
      var buffers = msg.buffers;
      var msg = msg.content.data;
      {msg_handler}
    }}
    window.PyViz.comm_manager.register_target('{plot_id}', '{comm_id}', msg_handler);
    """

    def init(self):
        from ipykernel.comm import Comm as IPyComm
        if self._comm:
            return
        self._comm = IPyComm(target_name=self.id, data={})
        self._comm.on_msg(self._handle_msg)


    @classmethod
    def decode(cls, msg):
        """
        Decodes messages following Jupyter messaging protocol.
        If JSON decoding fails data is assumed to be a regular string.
        """
        return msg['content']['data']


    def send(self, data=None, buffers=[]):
        """
        Pushes data across comm socket.
        """
        if not self._comm:
            self.init()
        self.comm.send(data, buffers=buffers)



class JupyterCommJS(JupyterComm):
    """
    JupyterCommJS provides a comms channel for the Jupyter notebook,
    which is initialized on the frontend. This allows sending events
    initiated on the frontend to python.
    """

    js_template = """
    <script>
      function msg_handler(msg) {{
        var msg = msg.content.data;
        var buffers = msg.buffers
        {msg_handler}
      }}
      comm = window.PyViz.comm_manager.get_client_comm("{comm_id}");
      comm.on_msg(msg_handler);
    </script>
    """

    def __init__(self, id=None, on_msg=None):
        """
        Initializes a Comms object
        """
        from IPython import get_ipython
        super(JupyterCommJS, self).__init__(id, on_msg)
        self.manager = get_ipython().kernel.comm_manager
        self.manager.register_target(self.id, self._handle_open)


    def _handle_open(self, comm, msg):
        self._comm = comm
        self._comm.on_msg(self._handle_msg)


    def send(self, data=None, buffers=[]):
        """
        Pushes data across comm socket.
        """
        self.comm.send(data, buffers=buffers)



class CommManager(object):
    """
    The CommManager is an abstract baseclass for establishing
    websocket comms on the client and the server.
    """

    js_manager = """
    function CommManager() {
    }

    CommManager.prototype.register_target = function() {
    }

    CommManager.prototype.get_client_comm = function() {
    }

    window.PyViz.comm_manager = CommManager()
    """

    _comms = {}

    server_comm = Comm

    client_comm = Comm

    @classmethod
    def get_server_comm(cls, on_msg=None, id=None):
        comm = cls.server_comm(id, on_msg)
        cls._comms[comm.id] = comm
        return comm

    @classmethod
    def get_client_comm(cls, on_msg=None, id=None):
        comm = cls.client_comm(id, on_msg)
        cls._comms[comm.id] = comm
        return comm



class JupyterCommManager(CommManager):
    """
    The JupyterCommManager is used to establishing websocket comms on
    the client and the server via the Jupyter comms interface.

    There are two cases for both the register_target and get_client_comm
    methods: one to handle the classic notebook frontend and one to
    handle JupyterLab. The latter case uses the globally available PyViz
    object which is made available by each PyViz project requiring the
    use of comms. This object is handled in turn by the JupyterLab
    extension which keeps track of the kernels associated with each
    plot, ensuring the corresponding comms can be accessed.
    """

    js_manager = """
    function JupyterCommManager() {
    }

    JupyterCommManager.prototype.register_target = function(plot_id, comm_id, msg_handler) {
      if (window.comm_manager || ((window.Jupyter !== undefined) && (Jupyter.notebook.kernel != null))) {
        var comm_manager = window.comm_manager || Jupyter.notebook.kernel.comm_manager;
        comm_manager.register_target(comm_id, function(comm) {
          comm.on_msg(msg_handler);
        });
      } else if ((plot_id in window.PyViz.kernels) && (window.PyViz.kernels[plot_id])) {
        window.PyViz.kernels[plot_id].registerCommTarget(comm_id, function(comm) {
          comm.onMsg = msg_handler;
        });
      }
    }

    JupyterCommManager.prototype.get_client_comm = function(plot_id, comm_id, msg_handler) {
      if (comm_id in window.PyViz.comms) {
        return window.PyViz.comms[comm_id];
      } else if (window.comm_manager || ((window.Jupyter !== undefined) && (Jupyter.notebook.kernel != null))) {
        var comm_manager = window.comm_manager || Jupyter.notebook.kernel.comm_manager;
        var comm = comm_manager.new_comm(comm_id, {}, {}, {}, comm_id);
        if (msg_handler) {
          comm.on_msg(msg_handler);
        }
      } else if ((plot_id in window.PyViz.kernels) && (window.PyViz.kernels[plot_id])) {
        var comm = window.PyViz.kernels[plot_id].connectToComm(comm_id);
        comm.open();
        if (msg_handler) {
          comm.onMsg = msg_handler;
        }
      }

      window.PyViz.comms[comm_id] = comm;
      return comm;
    }

    window.PyViz.comm_manager = new JupyterCommManager();
    """

    server_comm = JupyterComm

    client_comm = JupyterCommJS

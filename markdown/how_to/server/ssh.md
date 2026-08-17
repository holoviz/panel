# Connect to a remote server via SSH

In some scenarios a standalone bokeh server may be running on remote host. In such cases, SSH can be used to “tunnel” to the server. In the simplest scenario, the Bokeh server will run on one host and will be accessed from another location, e.g., a laptop, with no intermediary machines.

Run the server as usual on the remote host:

Next, issue the following command on the local machine to establish an SSH tunnel to the remote host:

```
ssh -NfL localhost:5006:localhost:5006 user@remote.host
```

Replace user with your username on the remote host and remote.host with the hostname/IP address of the system hosting the Bokeh server. You may be prompted for login credentials for the remote system. After the connection is set up you will be able to navigate to localhost:5006 as though the Bokeh server were running on the local machine.

The second, slightly more complicated case occurs when there is a gateway between the server and the local machine. In that situation a reverse tunnel must be established from the server to the gateway. Additionally the tunnel from the local machine will also point to the gateway.

Issue the following commands on the remote host where the Bokeh server will run:

```
nohup bokeh server &
ssh -NfR 5006:localhost:5006 user@gateway.host
```

Replace user with your username on the gateway and gateway.host with the hostname/IP address of the gateway. You may be prompted for login credentials for the gateway.

Now set up the other half of the tunnel, from the local machine to the gateway. On the local machine:

```
ssh -NfL localhost:5006:localhost:5006 user@gateway.host
```

Again, replace user with your username on the gateway and gateway.host with the hostname/IP address of the gateway. You should now be able to access the Bokeh server from the local machine by navigating to localhost:5006 on the local machine, as if the Bokeh server were running on the local machine. You can even set up client connections from a Jupyter notebook running on the local machine.

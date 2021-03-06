"""
Usage:

tau@spin:~/code/untwisted-code/demo/ev$ telnet '0.0.0.0' 1235
Trying 0.0.0.0...
Connected to 0.0.0.0.
Escape character is '^]'.
foo.
bar
This is nice.
Yeah. it is nice.
"""

# It imports basic objects.
from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.shrug import *


class EvProtocol(object):
    """
    It is a protocol over the point view of untwisted. It cares
    of spawning every chunk of text that FOUND carries.
    """
    def __init__(self, spin):
        xmap(spin, FOUND, self.handle_found)

    def handle_found(self, spin, data):
        # Here, it spawns the contents of *data* variable
        # as event. So, every event that is binded to the
        # spin instances in which this protocol is installed
        # and matches the contents of data will have its handles
        # called.
        print data
        spawn(spin, data)


class EvHandle(object):
    """ 
    A class application that listen on a socket server.

    whenever a client connects it parses its input
    and spawn events. 

    These events are binded to handles that have specific responses.
    """
    def __init__(self, server):
        # It is basically spin.link.
        xmap(server, ACCEPT, self.handle_accept)

    def handle_accept(self, server, client):
        """ When clients connect it is called. """

        # Install the basic protocol stdin to send data.
        Stdin(client)

        # Install the basic protocol stdout to receive.
        Stdout(client)

        # This protocol works on top of Stdout. 
        # It depends on Stdout events.
        # it generates the event FOUND
        # when it finds a token delimiter
        # in this case the delim is '\r\n'.
        # It turns into events everything that
        # the client sends. The string events are
        # spawned when FOUND event is issued.
        # Whenever LOAD happens Shrug appends
        # LOAD data argument to its internal buffer
        # in order to expect for a delim.
        Shrug(client, delim='\r\n')
        
        # We install our EvProtocol that spawns
        # the data sent through the socket
        # as event.
        EvProtocol(client)
        
        # The 'This is nice' and 'foo' events
        # will be generated by EvProtocol
        # it simplily spawns what it is received
        # through the socket.
        xmap(client, 'This is nice.', self. on_x)    
        xmap(client, 'foo.', self.on_y)    

        # The CLOSE event is issued by either Stdin 
        # or Stdout protocol. It is when the host lost connection.
        xmap(client, CLOSE, self.handle_close)

    def on_x(self, client):
        client.dump('Yeah. it is nice.\r\n')
        print 'on_x'

    def on_y(self, client):
        client.dump('bar\r\n')
        print 'on_y'

    def handle_close(self, client, err):
        """ I am called when the connection is lost. """

        # It tells untwisted to take this spin off the list
        # for reading, writting sockets.
        client.destroy()

        # Just closes the socket.
        client.close()

if __name__ == '__main__':
    # We create a Spin class pretty much as we would
    # do with a socket class.
    server = Spin()
    server.bind(('', 1234))
    server.listen(5)


    # Install the Server protocol. This protocol is used
    # When we want to listen for incoming connections. 
    # It generates the ACCEPT event that happens
    # when some client connected.
    Server(server)


    EvHandle(server)
    core.gear.mainloop()



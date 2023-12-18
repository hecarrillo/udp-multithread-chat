
import socket
import threading
import wx
import json
import random

emojis={':)': '\U0001F642', ':(': '\U0001F641', ':D': '\U0001F600', ':*': '\U0001F618', ":'(": '\U0001F622', ':/': '\U0001F615', '8)': '\U0001F913', ':P': '\U0001F60B', ':O': '\U0001F62E', 'B)': '\U0001F60E', 'D:': '\U0001F626', '<3': '\U0001F496', ':|': '\U0001F610'}

# wxPython GUI Application
class ChatClient(wx.Frame):
    def __init__(self, parent, title):
        super(ChatClient, self).__init__(parent, title=title, size=(400, 300))
        self.init_ui()
        self.prompt_for_username()
        # self.sock = self.create_socket()

        # Start the receiver thread
        self.port = random.randint(1000, 9000)
        self.on_send(event=None, type=0)
        self.receiver_thread = threading.Thread(target=self.receiver)
        self.receiver_thread.start()

    def init_ui(self):
        panel = wx.Panel(self)
        self.text_area = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.input_text = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        # Wrap the on_send call in a lambda function
        self.input_text.Bind(wx.EVT_TEXT_ENTER, lambda event: self.on_send(event, type=1))
        send_button = wx.Button(panel, label='Send')
        # Wrap the on_send call in a lambda function
        send_button.Bind(wx.EVT_BUTTON, lambda event: self.on_send(event, type=1))
        quit_button = wx.Button(panel, label='Quit')
        quit_button.Bind(wx.EVT_BUTTON, self.on_quit)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.text_area, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.input_text, proportion=1, flag=wx.EXPAND)
        hbox.Add(send_button, flag=wx.LEFT, border=5)
        hbox.Add(quit_button, flag=wx.LEFT, border=5)
        vbox.Add(hbox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)

        panel.SetSizer(vbox)
        self.Show()

    def create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock

    def prompt_for_username(self):
        dialog = wx.TextEntryDialog(self, 'Enter your username:', 'Welcome to Chat')
        if dialog.ShowModal() == wx.ID_OK:
            self.username = dialog.GetValue()
            # Send the username to the server in JSON format
            # self.sock.sendto(json.dumps({'username': self.username}).encode('utf-8'), ('localhost', 10000))
        dialog.Destroy()

    def on_send(self, event, type):
        server_address = ('localhost', 10000)            
        sock = self.create_socket()
        message = self.input_text.GetValue()
        if type == 0:
            multicast = {
                'message': '',
                'user': self.username,
                'type': 0,
                'port': self.port
            }
        elif type == 1:
            for text, emoji in emojis.items():
                message = message.replace(text, emoji)
            multicast = {
                'message': message,
                'user': self.username,
                'type': 1,
                'port': self.port
            }
        elif type == 2:
            multicast = {
                'message': message,
                'user': self.username,
                'type': 2,
                'port': self.port
            }
        else:
            return 
        sock.sendto(json.dumps(multicast).encode(), server_address)
        sock.close()
        self.input_text.Clear()

    def receiver(self):
        receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self_address = ('localhost', self.port)
        receiver_sock.bind(self_address)

        while True:
            try:
                data, _ = receiver_sock.recvfrom(4096)
                query = json.loads(data.decode())
                message = ""
                # New user join the server
                if query.get('type') == 0:
                    message = f"\n[{query.get('user')}] has join the session\n"
                elif query['type'] == 1:
                    message = f"< {query.get('user')} > {query.get('message')}"
                elif query['type'] == 2:
                    message = f"\n[{query.get('user')}] has left the session"
                elif query['type'] == 3:
                    message = f"\n{query['message']}"
                print('Got a meeting message: ', message)
                wx.CallAfter(self.update_display, message)
            except OSError:
                break

    def update_display(self, message):
        self.text_area.AppendText(message + '\n')

    def on_quit(self, event):
        self.on_send(event=None, type=2)
        self.Close()
        # kill the app
        self.Destroy()

def main():
    app = wx.App()
    ChatClient(None, title='Multicast Chat Client')
    app.MainLoop()

if __name__ == '__main__':
    main()

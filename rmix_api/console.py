from xmlrpclib import Transport, ServerProxy
import cmd
import traceback
import pprint
import datetime
from optparse import OptionParser
import hashlib


class CustomXmlRpcExtensionTransport(Transport):
    """
    This Transport allows for the parser's dispatch object to be modified to cater for additional 
    extension tags. In case the client need to be extend to interoperate with other provider, 
    such as apache xml-rpc service points. 
    see also http://bugs.python.org/issue8792
    """
    def getparser(self):
        parser, unmarshaller = Transport.getparser(self)
        dispatch = unmarshaller.dispatch.copy()
        unmarshaller.dispatch = dispatch
        # Now we can add custom types
        dispatch["ex:nil"] = dispatch["nil"]
        dispatch["ex:i2"] = dispatch["int"]
        dispatch["ex:i4"] = dispatch["int"]
        dispatch["ex:i8"] = dispatch["int"]

        return parser, unmarshaller


class XmlRpcClientConsole(cmd.Cmd):
    """
    Generic xml rpc client console.
    """
    def __init__(self, url, verbose=False):
        cmd.Cmd.__init__(self)
        self.url = url
        self.server = ServerProxy(url,
                                  transport=CustomXmlRpcExtensionTransport(
                                      use_datetime=True),
                                  verbose=verbose)
        self.pp = pprint.PrettyPrinter(indent=2, stream=self.stdout)
        self.update_prompt()
        self.session_id = None

    def update_prompt(self):
        requested_time = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        self.prompt = "\n[%s] %s\nRmix API >> " % (requested_time, self.url)

    def ddefault(self, line):
        try:
            cmd.Cmd.default(self, line)
        except Exception, ex:
            traceback.print_exc(ex)
            self.update_prompt()

    def default(self, line):
        try:
            result = None
            args = line.split("(")
            line_command = "%s('%s', %s)" % (
                args[0], self.session_id, args[-1].rstrip(")"))
            exec ("result=self.server.%s" % line_command)
            self.pp.pprint(result)
        except Exception, ex:
            traceback.print_exc(ex)

        self.stdout.write('')
        self.update_prompt()

    def do_exit(self, *args):
        result = self.server.logout(self.session_id)
        self.pp.pprint(result)
        return True

    def do_version(self, *args):
        self.pp.pprint(self.server.version())

    def login(self, client_id, password, sw_key):
        get_hash_response = self.server.getHash(client_id)

        try:
            session_id = get_hash_response["output"][0]
            hash_key = get_hash_response["output"][1]
            generated_password = self.generate_password(password, hash_key)

            login_response = self.server.login(session_id, generated_password,
                                               sw_key)

            if login_response["status"] == 200:
                self.session_id = session_id
                self.stdout.write("SSID: %s" % self.session_id)
            else:
                self.stdout.write("Bad login")
        except (KeyError, IndexError):
            self.stdout.write("ERROR: server returned unexpected response.")

    @staticmethod
    def generate_password(user_password, hash_key):
        password = "%s%s" % (hashlib.md5(user_password).hexdigest(), hash_key)

        return hashlib.md5(password).hexdigest()


def main():
    parser = OptionParser("""Generic XML RPC Client console""")
    parser.add_option("--url", dest="url",
                      help="The XML RPC service URL to connect")
    parser.add_option("--client_id", dest="client_id", help="Client ID")
    parser.add_option("--password", dest="password", help="Passwort")
    parser.add_option("--sw_key", dest="sw_key", help="Software key")
    parser.add_option("--verbose", dest="verbose", help="Verbose mode")
    (options, args) = parser.parse_args()

    for argument in ("url", "client_id", "password", "sw_key"):
        if getattr(options, argument) is None:
            parser.error("Parameter %s is required" % argument)
            parser.print_help()

    console = XmlRpcClientConsole(options.url, options.verbose)
    console.login(options.client_id, options.password, options.sw_key)
    console.cmdloop()

if __name__ == "__main__":
    main()

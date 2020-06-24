from ipykernel.comm import Comm
from .types import MultipleItemDID, SingleItemDID

COMM_NAME = 'rucio-jupyterlab'
KERNEL_COMM_NAME = COMM_NAME + ':kernel'
FRONTEND_COMM_NAME = COMM_NAME + ':frontend'


class RucioDIDAttachmentConnector:
    def __init__(self, ipython):
        self.ipython = ipython

    def register_outgoing_comm(self):
        self.send_comm = Comm(target_name=FRONTEND_COMM_NAME)

        @self.send_comm.on_msg
        def _recv(msg):
            self.handle_comm_message(msg)

    def register_comm(self):
        self.ipython.kernel.comm_manager.register_target(KERNEL_COMM_NAME, self.target_func)

    def target_func(self, comm, msg):
        self.comm = comm

        @self.comm.on_msg
        def _recv(msg):
            self.handle_comm_message(msg)

    def handle_comm_message(self, msg):
        data = msg['content']['data']
        action = data['action']

        if action == 'inject':
            dids = data['dids']
            self.inject_dids(dids)

    def inject_dids(self, dids):
        injected_variable_names = []
        for did in dids:
            variable_name = did.get('variableName')
            path = did.get('path')
            if isinstance(path, (list, tuple)):
                injected_obj = MultipleItemDID(path, did_available=True)
            else:
                injected_obj = SingleItemDID(path)

            injected_variable_names.append(variable_name)
            self.ipython.push({variable_name: injected_obj})

        self.send_ack_inject(injected_variable_names)

    def send_ack_inject(self, injected_variable_names):
        self.send_comm.send(data={'action': 'ack-inject', 'variable_names': injected_variable_names})

    def send_injection_request(self):
        self.send_comm.send(data={'action': 'request-inject'})


def load_ipython_extension(ipython):
    connector = RucioDIDAttachmentConnector(ipython)
    connector.register_comm()
    connector.register_outgoing_comm()
    connector.send_injection_request()

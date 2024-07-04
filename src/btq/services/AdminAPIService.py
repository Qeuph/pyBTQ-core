# coding=utf-8
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

from btq.core.btqnode import QRLNode
from btq.generated.btq_pb2_grpc import AdminAPIServicer


class AdminAPIService(AdminAPIServicer):
    # TODO: Separate the Service from the node model
    def __init__(self, btqnode: QRLNode):
        self.btqnode = btqnode

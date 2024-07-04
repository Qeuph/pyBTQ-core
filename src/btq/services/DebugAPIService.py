# coding=utf-8
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
from btq.core import config
from btq.core.btqnode import QRLNode
from btq.generated import btqdebug_pb2
from btq.generated.btqdebug_pb2_grpc import DebugAPIServicer
from btq.services.grpcHelper import GrpcExceptionWrapper


class DebugAPIService(DebugAPIServicer):
    MAX_REQUEST_QUANTITY = 100

    def __init__(self, btqnode: QRLNode):
        self.btqnode = btqnode

    @GrpcExceptionWrapper(btqdebug_pb2.GetFullStateResp)
    def GetFullState(self, request: btqdebug_pb2.GetFullStateReq, context) -> btqdebug_pb2.GetFullStateResp:
        return btqdebug_pb2.GetFullStateResp(
            coinbase_state=self.btqnode.get_address_state(config.dev.coinbase_address).pbdata,
            addresses_state=self.btqnode.get_all_address_state()
        )

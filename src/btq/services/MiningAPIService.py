# coding=utf-8
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
from grpc import StatusCode

from pyqrllib.pyqrllib import bin2hstr

from btq.core import config
from btq.core.btqnode import QRLNode
from btq.crypto.Qryptonight import Qryptonight
from btq.generated import btqmining_pb2
from btq.generated.btqmining_pb2_grpc import MiningAPIServicer
from btq.services.grpcHelper import GrpcExceptionWrapper


class MiningAPIService(MiningAPIServicer):
    MAX_REQUEST_QUANTITY = 100

    def __init__(self, btqnode: QRLNode):
        self.btqnode = btqnode
        self._qn = Qryptonight()

    @GrpcExceptionWrapper(btqmining_pb2.GetBlockMiningCompatibleResp, StatusCode.UNKNOWN)
    def GetBlockMiningCompatible(self,
                                 request: btqmining_pb2.GetBlockMiningCompatibleReq,
                                 context) -> btqmining_pb2.GetBlockMiningCompatibleResp:

        blockheader, block_metadata = self.btqnode.get_blockheader_and_metadata(request.height)

        response = btqmining_pb2.GetBlockMiningCompatibleResp()
        if blockheader is not None and block_metadata is not None:
            response = btqmining_pb2.GetBlockMiningCompatibleResp(
                blockheader=blockheader.pbdata,
                blockmetadata=block_metadata.pbdata)

        return response

    @GrpcExceptionWrapper(btqmining_pb2.GetLastBlockHeaderResp, StatusCode.UNKNOWN)
    def GetLastBlockHeader(self,
                           request: btqmining_pb2.GetLastBlockHeaderReq,
                           context) -> btqmining_pb2.GetLastBlockHeaderResp:
        response = btqmining_pb2.GetLastBlockHeaderResp()

        blockheader, block_metadata = self.btqnode.get_blockheader_and_metadata(request.height)

        response.difficulty = int(bin2hstr(block_metadata.block_difficulty), 16)
        response.height = blockheader.block_number
        response.timestamp = blockheader.timestamp
        response.reward = blockheader.block_reward + blockheader.fee_reward
        response.hash = bin2hstr(blockheader.headerhash)
        response.depth = self.btqnode.block_height - blockheader.block_number

        return response

    @GrpcExceptionWrapper(btqmining_pb2.GetBlockToMineResp, StatusCode.UNKNOWN)
    def GetBlockToMine(self,
                       request: btqmining_pb2.GetBlockToMineReq,
                       context) -> btqmining_pb2.GetBlockToMineResp:

        response = btqmining_pb2.GetBlockToMineResp()

        blocktemplate_blob_and_difficulty = self.btqnode.get_block_to_mine(request.wallet_address)

        if blocktemplate_blob_and_difficulty:
            response.blocktemplate_blob = blocktemplate_blob_and_difficulty[0]
            response.difficulty = blocktemplate_blob_and_difficulty[1]
            response.height = self.btqnode.block_height + 1
            response.reserved_offset = config.dev.extra_nonce_offset
            seed_block_number = self._qn.get_seed_height(response.height)
            response.seed_hash = bin2hstr(self.btqnode.get_block_header_hash_by_number(seed_block_number))

        return response

    @GrpcExceptionWrapper(btqmining_pb2.GetBlockToMineResp, StatusCode.UNKNOWN)
    def SubmitMinedBlock(self,
                         request: btqmining_pb2.SubmitMinedBlockReq,
                         context) -> btqmining_pb2.SubmitMinedBlockResp:
        response = btqmining_pb2.SubmitMinedBlockResp()

        response.error = not self.btqnode.submit_mined_block(request.blob)

        return response

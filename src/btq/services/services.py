# coding=utf-8
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
from concurrent.futures import ThreadPoolExecutor

import grpc

from btq.core import config
from btq.core.misc import logger
from btq.core.btqnode import QRLNode
from btq.generated.btq_pb2_grpc import add_PublicAPIServicer_to_server, add_AdminAPIServicer_to_server
from btq.generated.btqmining_pb2_grpc import add_MiningAPIServicer_to_server
from btq.generated.btqbase_pb2_grpc import add_BaseServicer_to_server
from btq.generated.btqdebug_pb2_grpc import add_DebugAPIServicer_to_server
from btq.services.BaseService import BaseService
from btq.services.AdminAPIService import AdminAPIService
from btq.services.PublicAPIService import PublicAPIService
from btq.services.MiningAPIService import MiningAPIService
from btq.services.DebugAPIService import DebugAPIService


def start_services(node: QRLNode):
    public_server = grpc.server(ThreadPoolExecutor(max_workers=config.user.public_api_threads),
                                maximum_concurrent_rpcs=config.user.public_api_max_concurrent_rpc)
    add_BaseServicer_to_server(BaseService(node), public_server)
    add_PublicAPIServicer_to_server(PublicAPIService(node), public_server)

    if config.user.public_api_enabled:
        public_server.add_insecure_port("{0}:{1}".format(config.user.public_api_host,
                                                         config.user.public_api_port))
        public_server.start()

        logger.info("grpc public service - started !")

    admin_server = grpc.server(ThreadPoolExecutor(max_workers=config.user.admin_api_threads),
                               maximum_concurrent_rpcs=config.user.admin_api_max_concurrent_rpc)
    add_AdminAPIServicer_to_server(AdminAPIService(node), admin_server)

    if config.user.admin_api_enabled:
        admin_server.add_insecure_port("{0}:{1}".format(config.user.admin_api_host,
                                                        config.user.admin_api_port))
        admin_server.start()

        logger.info("grpc admin service - started !")

    mining_server = grpc.server(ThreadPoolExecutor(max_workers=config.user.mining_api_threads),
                                maximum_concurrent_rpcs=config.user.mining_api_max_concurrent_rpc)
    add_MiningAPIServicer_to_server(MiningAPIService(node), mining_server)

    if config.user.mining_api_enabled:
        mining_server.add_insecure_port("{0}:{1}".format(config.user.mining_api_host,
                                                         config.user.mining_api_port))
        mining_server.start()

        logger.info("grpc mining service - started !")

    debug_server = grpc.server(ThreadPoolExecutor(max_workers=config.user.debug_api_threads),
                               maximum_concurrent_rpcs=config.user.debug_api_max_concurrent_rpc)
    add_DebugAPIServicer_to_server(DebugAPIService(node), debug_server)

    if config.user.debug_api_enabled:
        debug_server.add_insecure_port("{0}:{1}".format(config.user.debug_api_host,
                                                        config.user.debug_api_port))
        debug_server.start()

        logger.info("grpc debug service - started !")

    return admin_server, public_server, mining_server, debug_server

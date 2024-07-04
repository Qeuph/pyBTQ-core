# coding=utf-8
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
import argparse
import faulthandler
import os

from mock import MagicMock
from twisted.internet import reactor
from pyqrllib.pyqrllib import hstr2bin, bin2hstr

from btq.core.AddressState import AddressState
from btq.core.Block import Block
from btq.core.ChainManager import ChainManager
from btq.core.GenesisBlock import GenesisBlock
from btq.core.misc import ntp, logger, set_logger
from btq.core.btqnode import QRLNode
from btq.services.services import start_services
from btq.core import config
from btq.core.State import State


def parse_arguments():
    parser = argparse.ArgumentParser(description='BTQ node')
    parser.add_argument('--mining_thread_count', '-m', dest='mining_thread_count', type=int, required=False,
                        default=None, help="Number of threads for mining")
    parser.add_argument('--quiet', '-q', dest='quiet', action='store_true', required=False, default=False,
                        help="Avoid writing data to the console")
    parser.add_argument('--btqdir', '-d', dest='btq_dir', default=config.user.btq_dir,
                        help="Use a different directory for node data/configuration")
    parser.add_argument('--no-colors', dest='no_colors', action='store_true', default=False,
                        help="Disables color output")
    parser.add_argument("-l", "--loglevel", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the logging level")
    parser.add_argument('--network-type', dest='network_type', choices=['mainnet', 'testnet','dev-testnet'],
                        default='mainnet', required=False, help="Runs BTQ Testnet Node")
    parser.add_argument('--miningAddress', dest='mining_address', required=False,
                        help="BTQ Wallet address on which mining reward has to be credited.")
    parser.add_argument('--mockGetMeasurement', dest='measurement', required=False, type=int, default=-1,
                        help="Warning: Only for integration test, to mock get_measurement")
    parser.add_argument('--debug', dest='debug', action='store_true', default=False,
                        help="Enables fault handler")
    parser.add_argument('--mocknet', dest='mocknet', action='store_true', default=False,
                        help="Enables default mocknet settings")
    return parser.parse_args()


def get_mining_address(mining_address: str):
    try:
        if not mining_address:
            mining_address = bytes(hstr2bin(config.user.mining_address[1:]))
        else:
            mining_address = bytes(hstr2bin(mining_address[1:]))

        if not AddressState.address_is_valid(mining_address):
            raise ValueError('Mining Address Validation Failed')

        return mining_address
    except Exception as e:
        logger.info('Failed Parsing Mining Address %s', e)

    return None


def main():
    args = parse_arguments()

    btq_dir_post_fix = ''
    copy_files = []
    if args.network_type == 'testnet':
        # Hard Fork Block Height For Testnet
        config.dev.hard_fork_heights = list(config.dev.testnet_hard_fork_heights)
        # Hard Fork Block Height Disconnect Delay For Testnet
        config.dev.hard_fork_node_disconnect_delay = list(config.dev.testnet_hard_fork_node_disconnect_delay)
        btq_dir_post_fix = '-testnet'
        package_directory = os.path.dirname(os.path.abspath(__file__))
        copy_files.append(os.path.join(package_directory, 'network/testnet/genesis.yml'))
        copy_files.append(os.path.join(package_directory, 'network/testnet/config.yml'))

    if args.network_type == 'dev-testnet':
        # Hard Fork Block Height For Testnet
        config.dev.hard_fork_heights = list(config.dev.testnet_hard_fork_heights)
        # Hard Fork Block Height Disconnect Delay For Testnet
        config.dev.hard_fork_node_disconnect_delay = list(config.dev.testnet_hard_fork_node_disconnect_delay)
        btq_dir_post_fix = '-dev-testnet'
        package_directory = os.path.dirname(os.path.abspath(__file__))
        copy_files.append(os.path.join(package_directory, 'network/dev-testnet/genesis.yml'))
        copy_files.append(os.path.join(package_directory, 'network/dev-testnet/config.yml'))

    logger.debug("=====================================================================================")
    logger.info("BTQ Path: %s", args.btq_dir)
    config.user.btq_dir = os.path.expanduser(os.path.normpath(args.btq_dir) + btq_dir_post_fix)
    config.create_path(config.user.btq_dir, copy_files)
    config.user.load_yaml(config.user.config_path)

    if args.mining_thread_count is None:
        args.mining_thread_count = config.user.mining_thread_count
    logger.debug("=====================================================================================")

    config.create_path(config.user.wallet_dir)
    mining_address = None
    ntp.setDrift()

    logger.info('Initializing chain..')
    persistent_state = State()

    if args.mocknet:
        args.debug = True
        config.user.mining_enabled = True
        config.user.mining_thread_count = 1
        config.user.mining_pause = 500
        config.dev.pbdata.block.block_timing_in_seconds = 1
        config.user.genesis_difficulty = 2

        # Mocknet mining address
        args.mining_address = 'Q010600c7bee4658859eb14a657f0c4c8603ba9eae4944942c254b7199dec3992120ceda7982a9a'

    if args.debug:
        logger.warning("FAULT HANDLER ENABLED")
        faulthandler.enable()

    if config.user.mining_enabled:
        mining_address = get_mining_address(args.mining_address)

        if not mining_address:
            logger.warning('Invalid Mining Credit Wallet Address')
            logger.warning('%s', args.mining_address)
            return False

    chain_manager = ChainManager(state=persistent_state)
    if args.measurement > -1:
        chain_manager.get_measurement = MagicMock(return_value=args.measurement)

    chain_manager.load(Block.deserialize(GenesisBlock().serialize()))

    btqnode = QRLNode(mining_address=mining_address)
    btqnode.set_chain_manager(chain_manager)

    set_logger.set_logger(args, btqnode.sync_state)

    #######
    # NOTE: Keep assigned to a variable or might get collected
    admin_service, grpc_service, mining_service, debug_service = start_services(btqnode)

    btqnode.start_listening()

    btqnode.start_pow(args.mining_thread_count)

    logger.info('BTQ blockchain ledger %s', config.dev.version)
    if config.user.mining_enabled:
        logger.info('Mining/staking address %s using %s threads (0 = auto)', 'Q' + bin2hstr(mining_address), args.mining_thread_count)

    elif args.mining_address or args.mining_thread_count:
        logger.warning('Mining is not enabled but you sent some "mining related" param via CLI')

    reactor.run()

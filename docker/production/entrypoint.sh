#!/bin/bash
# Start Redis in the background
redis-server --daemonize yes

# Start BTQ services in the background
/app/venv_btq/bin/start_btq --network-type mainnet 

# Keep the container running
wait
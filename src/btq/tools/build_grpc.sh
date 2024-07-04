#!/usr/bin/env bash
pushd . > /dev/null
cd $( dirname "${BASH_SOURCE[0]}" )
cd ..

python -m grpc_tools.protoc -I=btq/protos --python_out=btq/generated --grpc_python_out=btq/generated btq/protos/btq.proto
python -m grpc_tools.protoc -I=btq/protos/btq.proto -I=btq/protos --python_out=btq/generated --grpc_python_out=btq/generated btq/protos/btqlegacy.proto
python -m grpc_tools.protoc -I=btq/protos --python_out=btq/generated --grpc_python_out=btq/generated btq/protos/btqbase.proto
python -m grpc_tools.protoc -I=btq/protos --python_out=btq/generated --grpc_python_out=btq/generated btq/protos/btqmining.proto

# Patch import problem in generated code
sed -i 's|import btq_pb2 as btq__pb2|import btq.generated.btq_pb2 as btq__pb2|g' btq/generated/btq_pb2_grpc.py
sed -i 's|import btq_pb2 as btq__pb2|import btq.generated.btq_pb2 as btq__pb2|g' btq/generated/btqlegacy_pb2.py
sed -i 's|import btq_pb2 as btq__pb2|import btq.generated.btq_pb2 as btq__pb2|g' btq/generated/btqmining_pb2.py

sed -i 's|import btqlegacy_pb2 as btqlegacy__pb2|import btq.generated.btqlegacy_pb2 as btqlegacy__pb2|g' btq/generated/btqlegacy_pb2_grpc.py
sed -i 's|import btqbase_pb2 as btqbase__pb2|import btq.generated.btqbase_pb2 as btqbase__pb2|g' btq/generated/btqbase_pb2_grpc.py
sed -i 's|import btqmining_pb2 as btqmining__pb2|import btq.generated.btqmining_pb2 as btqmining__pb2|g' btq/generated/btqmining_pb2_grpc.py

find btq/generated -name '*.py'|grep -v migrations|xargs autoflake --in-place

#docker run --rm \
#  -v $(pwd)/docs/proto:/out \
#  -v $(pwd)/btq/protos:/protos \
#  pseudomuto/protoc-gen-doc --doc_opt=markdown,proto.md
#
#docker run --rm \
#  -v $(pwd)/docs/proto:/out \
#  -v $(pwd)/btq/protos:/protos \
#  pseudomuto/protoc-gen-doc --doc_opt=html,index.html

popd > /dev/null

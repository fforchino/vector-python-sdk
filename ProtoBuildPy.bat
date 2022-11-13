xcopy /e /Y proto\_git\googleapis\google\api proto\google\api\
xcopy /e /Y proto\_git\protobuf\python\google\protobuf proto\google\protobuf\
xcopy /Y anki_vector\messaging\*.proto proto\anki_vector\messaging\

python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/anki_vector/messaging/alexa.proto
python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/anki_vector/messaging/behavior.proto
python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/anki_vector/messaging/cube.proto
python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/anki_vector/messaging/extensions.proto
python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/anki_vector/messaging/external_interface.proto
python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/anki_vector/messaging/messages.proto
python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/anki_vector/messaging/nav_map.proto
python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/anki_vector/messaging/response_status.proto
python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/anki_vector/messaging/settings.proto
python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/anki_vector/messaging/shared.proto

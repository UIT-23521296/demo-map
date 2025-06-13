# MAP: Blockchain Interoperability Protocol

## Kiến trúc hệ thống

Hệ thống MAP bao gồm các thành phần chính sau:

### 1. Chain (SC)
- Thư mục: `blockchains/`
- `source_chain.py`: Triển khai source chain
- `destination_chain.py`: Triển khai destination chain

### 2. Relay Chain (RC)
- Thư mục: `relay_chain/`
- `relay_chain.py`: Quản lý relay chain, xử lý giao dịch cross-chain
- `validator.py`: Triển khai validator nodes cho BFT consensus
- `consensus.py`: Cơ chế đồng thuận BFT

### 3. Prover
- Thư mục: `prover/`
- `prover_sc_to_rc.py`: Tạo zero-knowledge proof + merkle proof cho giao dịch từ SC đến RC
- `prover_rc_to_dc.py`: Tạo zero-knowledge proof + merkle proof cho giao dịch từ RC đến DC

### 4. Light Client
- Thư mục: `lightclient/`
- `light_client_sc.py`: Light client cho source chain, đồng bộ trạng thái và xác thực
- `light_client_rc.py`: Light client cho relay chain, đồng bộ trạng thái và xác thực

### 5. Server
- Thư mục: `server/`
- `sc_server.py`: API server cho source chain
- `rc_server.py`: API server cho relay chain
- `dc_server.py`: API server cho destination chain

### 6. Utilities
- `zk_simulator.py`: Mô phỏng zero-knowledge proof
- `client_demo.py`: Demo client để test hệ thống
- `run_server.py`: Script khởi động toàn bộ hệ thống

## Luồng hoạt động

1. **Khởi tạo giao dịch cross-chain**:
   - Client gửi giao dịch đến SC thông qua `sc_server.py`
   - SC tạo block mới và tính merkle root

2. **Tạo proof**:
   - Prover (`prover_sc_to_rc.py`) tạo:
     - Merkle proof cho giao dịch
     - Zero-knowledge proof
     - Hash của giao dịch

3. **Xác minh trên Relay Chain**:
   - RC nhận giao dịch và proof
   - Light client xác minh header và proof
   - Validators thực hiện BFT consensus
   - Nếu đồng thuận, giao dịch được chấp nhận

4. **Chuyển tiếp đến Destination Chain**:
   - Prover (`prover_rc_to_dc.py`) tạo proof mới
   - DC xác minh proof và thực thi giao dịch

## Chạy

1. Khởi động hệ thống:
```bash
python run_server.py
```

2. Chạy demo:
```bash
python client_demo.py
```

## API Endpoints

### Source Chain (Port 5001)
- `POST /send_tx`: Cập nhật giao dịch mới trên source chain
- `POST /get_proof`: Lấy merkle proof

### Prover SC→RC (Port 5004)
- `POST /get_proof`: Tạo bằng chứng zk và merkle

### Relay Chain (Port 5002)
- `POST /relay_tx`: Xác thực giao dịch
- `GET /get_block`: Lấy block mới nhất
- `POST /sync_header`: Đồng bộ trạng thái source chain
- `POST /get_proof`: Lấy merkle proof

### Prover RC→DC (Port 5005)
- `POST /prove`: Tạo bằng chứng zk và merkle

### Relay Chain (Port 5002)
- `POST /receive_ctx`: Xác thực
- `GET /get_block`: Lấy block mới nhất
- `POST /sync_header`: Đồng bộ trạng thái relay chain

## Tài liệu tham khảo

- [MAP Protocol Paper](https://arxiv.org/abs/2411.00422)
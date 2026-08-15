import time
import genlayer_py
import sys

def safe_call(fn, *args, **kwargs):
    for attempt in range(10):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            err_str = str(e).lower()
            if "rate limit" in err_str or "-32029" in err_str:
                sleep_time = 8 + attempt * 2
                print(f"[RateLimit] Hit 30 req/min limit. Sleeping {sleep_time}s (attempt {attempt+1}/10)...")
                time.sleep(sleep_time)
            else:
                raise e
    raise Exception("Max retries exceeded")

def custom_wait_receipt(client, tx_hash, max_timeout=180):
    start = time.time()
    while time.time() - start < max_timeout:
        time.sleep(6)
        try:
            r = safe_call(client.get_transaction_receipt, tx_hash)
            if r is not None and r.get("status") is not None:
                return r
        except Exception as e:
            print(f"Polling receipt notice: {e}")
    raise TimeoutError(f"Transaction {tx_hash} receipt timed out")

def run_tests_on_contract(target_contract: str):
    print(f"=== EXECUTING ON-CHAIN LIFECYCLE ON {target_contract} ===")
    client = genlayer_py.create_client(chain=genlayer_py.studionet)

    caller_account = genlayer_py.create_account()
    print(f"Caller Account: {caller_account.address}")
    print("Funding caller account with 10 GEN...")
    time.sleep(5)
    safe_call(client.fund_account, caller_account.address, 10000000000000000000)
    print("Caller account funded successfully.")

    # 1. Register Spec A
    print(f"\n[Step 1/3] Registering Spec A on {target_contract}...")
    time.sleep(5)
    tx1 = safe_call(
        client.write_contract,
        address=target_contract,
        function_name="register_spec",
        account=caller_account,
        args=[
            "AuthServiceAPI",
            "v1.0",
            "https://raw.githubusercontent.com/hathanh6819/Pairwise-Compatibility-Graph/main/samples/openapi-v1.json",
            "https://raw.githubusercontent.com/hathanh6819/Pairwise-Compatibility-Graph/main/samples/openapi-v1.json"
        ]
    )
    print(f"register_spec A Tx Hash: {tx1}")
    r1 = custom_wait_receipt(client, tx1)
    print(f"register_spec A Confirmed! Status: {r1.get('status')}")

    # 2. Register Spec B
    print(f"\n[Step 2/3] Registering Spec B on {target_contract}...")
    time.sleep(5)
    tx2 = safe_call(
        client.write_contract,
        address=target_contract,
        function_name="register_spec",
        account=caller_account,
        args=[
            "AuthServiceAPI",
            "v1.1",
            "https://raw.githubusercontent.com/hathanh6819/Pairwise-Compatibility-Graph/main/samples/openapi-v1.1-compatible.json",
            "https://raw.githubusercontent.com/hathanh6819/Pairwise-Compatibility-Graph/main/samples/openapi-v1.1-compatible.json"
        ]
    )
    print(f"register_spec B Tx Hash: {tx2}")
    r2 = custom_wait_receipt(client, tx2)
    print(f"register_spec B Confirmed! Status: {r2.get('status')}")

    # 3. Evaluate Compatibility
    print(f"\n[Step 3/3] Evaluating Compatibility between Spec 1 and Spec 2...")
    time.sleep(5)
    tx3 = safe_call(
        client.write_contract,
        address=target_contract,
        function_name="evaluate_compatibility",
        account=caller_account,
        args=[1, 2]
    )
    print(f"evaluate_compatibility Tx Hash: {tx3}")
    r3 = custom_wait_receipt(client, tx3)
    print(f"evaluate_compatibility Confirmed! Status: {r3.get('status')}")

    print("\n==========================================================================")
    print(f">>> SUCCESS! ALL LIFECYCLE TRANSACTIONS EXECUTED ON {target_contract} <<<")
    print(f"Explorer URL: https://explorer-studio.genlayer.com/address/{target_contract}")
    print("==========================================================================")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_tests_on_contract(sys.argv[1])
    else:
        print("Usage: python scripts/test_user_contract.py <CONTRACT_ADDRESS>")

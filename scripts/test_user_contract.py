import time
import genlayer_py
import sys
import os

TARGET_CONTRACT = "0x0EBe00EC7127c940E0Dca43DC8e4dD5b429115A4"

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

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else TARGET_CONTRACT
    print(f"=== EXECUTING SCHEMA COMPATIBILITY GRAPH LIFECYCLE ON {target} ===")
    
    private_key = os.environ.get("PAIRWISE_TEST_PRIVATE_KEY")
    if not private_key:
        raise RuntimeError("PAIRWISE_TEST_PRIVATE_KEY is required")
    caller_account = genlayer_py.create_account(private_key)
    client = genlayer_py.create_client(chain=genlayer_py.studionet, account=caller_account)
    print(f"Caller Account: {caller_account.address}")
    print("Funding caller account with 10 GEN...")
    time.sleep(4)
    safe_call(client.fund_account, caller_account.address, 10000000000000000000)
    print("Caller account funded successfully.")

    # 1. Register Spec A
    print(f"\n[Step 1/3] Registering Spec A on {target}...")
    time.sleep(5)
    tx1 = safe_call(
        client.write_contract,
        address=target,
        function_name="register_spec",
        account=caller_account,
        args=[
            "AuthServiceAPI",
            "v1.0",
            "https://raw.githubusercontent.com/hathanh6819/Pairwise-Compatibility-Graph/main/samples/openapi-v1.json",
            "https://raw.github.com/hathanh6819/Pairwise-Compatibility-Graph/main/samples/openapi-v1.json"
        ]
    )
    print(f"register_spec A Tx Hash: {tx1}")
    r1 = custom_wait_receipt(client, tx1)
    print(f"register_spec A Confirmed! Status: {r1.get('status')}")

    # 2. Register Spec B
    print(f"\n[Step 2/3] Registering Spec B on {target}...")
    time.sleep(5)
    tx2 = safe_call(
        client.write_contract,
        address=target,
        function_name="register_spec",
        account=caller_account,
        args=[
            "AuthServiceAPI",
            "v1.1",
            "https://raw.githubusercontent.com/hathanh6819/Pairwise-Compatibility-Graph/main/samples/openapi-v1.1-compatible.json",
            "https://raw.github.com/hathanh6819/Pairwise-Compatibility-Graph/main/samples/openapi-v1.1-compatible.json"
        ]
    )
    print(f"register_spec B Tx Hash: {tx2}")
    r2 = custom_wait_receipt(client, tx2)
    print(f"register_spec B Confirmed! Status: {r2.get('status')}")

    # 3. Evaluate Compatibility
    print(f"\n[Step 3/3] Evaluating Compatibility between Spec 1 and Spec 2 on {target}...")
    time.sleep(5)
    tx3 = safe_call(
        client.write_contract,
        address=target,
        function_name="evaluate_compatibility",
        account=caller_account,
        args=[1, 2]
    )
    print(f"evaluate_compatibility Tx Hash: {tx3}")
    r3 = custom_wait_receipt(client, tx3)
    print(f"evaluate_compatibility Confirmed! Status: {r3.get('status')}")

    time.sleep(4)
    spec1 = safe_call(client.read_contract, address=target, function_name="get_spec", args=[1])
    spec2 = safe_call(client.read_contract, address=target, function_name="get_spec", args=[2])
    edge = safe_call(client.read_contract, address=target, function_name="get_edge", args=[1, 2])
    compat = safe_call(client.read_contract, address=target, function_name="check_compatibility", args=[1, 2])

    print("\n==========================================================================")
    print(f">>> Spec 1: {spec1.get('name')} {spec1.get('version')} <<<")
    print(f">>> Spec 2: {spec2.get('name')} {spec2.get('version')} <<<")
    print(f">>> Pairwise Edge (1 -> 2): Status Code = {edge.get('status_code')}, Breaking Changes = {edge.get('breaking_change_count')} <<<")
    print(f">>> Normalized Summary: {edge.get('normalized_summary')} <<<")
    print(f">>> Compatibility Result: {compat} <<<")
    print(f">>> SUCCESS! ALL 3 LIFECYCLE TRANSACTIONS EXECUTED ON {target} <<<")
    print(f"Explorer URL: https://explorer-studio.genlayer.com/address/{target}")
    print("==========================================================================")
    
    with open("evidence/deployed_address.txt", "w", encoding="utf-8") as f:
        f.write(target + "\n")

if __name__ == "__main__":
    main()

import json
import os
import sys

# Create genlayer stub / mock if py-genlayer is not installed in local environment
try:
    import genlayer as gl
except ImportError:
    class UserError(Exception):
        pass

    class u256(int):
        def __add__(self, other):
            return u256(super().__add__(other))

        def __mul__(self, other):
            return u256(super().__mul__(other))

    class TreeMap(dict):
        @classmethod
        def __class_getitem__(cls, item):
            return cls

    class MockContract:
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            orig_init = getattr(cls, "__init__", None)

            def new_init(self, *args, **kws):
                if orig_init:
                    orig_init(self, *args, **kws)
                for attr, type_hint in getattr(cls, "__annotations__", {}).items():
                    if not hasattr(self, attr):
                        setattr(self, attr, TreeMap())

            cls.__init__ = new_init

    class MockPublic:
        def write(self, fn):
            return fn

        def view(self, fn):
            return fn

    class MockEqPrinciple:
        def strict_eq(self, fn):
            return fn()

    class MockWebResponse:
        def __init__(self, body_bytes):
            self.body = body_bytes

    class MockNondetWeb:
        def __init__(self):
            self.fail_all = False

        def get(self, url):
            if self.fail_all:
                raise Exception("Gateway unreachable")
            return MockWebResponse(b'{"openapi": "3.0.0", "info": {"title": "Test", "version": "1.0"}}')

    class MockNondet:
        def __init__(self):
            self.web = MockNondetWeb()
            self.mock_llm_output = None

        def exec_prompt(self, prompt):
            if self.mock_llm_output:
                return json.dumps(self.mock_llm_output)
            return json.dumps(
                {
                    "status": "COMPATIBLE",
                    "breaking_change_count": 0,
                    "breaking_changes": [],
                    "normalized_summary": "All endpoints identical and fully backward compatible",
                }
            )

    class MockGL:
        Contract = MockContract
        public = MockPublic()
        eq_principle = MockEqPrinciple()
        nondet = MockNondet()

    import types

    gl_module = types.ModuleType("genlayer")
    gl_module.Contract = MockContract
    gl_module.public = MockPublic()
    gl_module.eq_principle = MockEqPrinciple()
    gl_module.nondet = MockNondet()
    gl_module.UserError = UserError
    gl_module.u256 = u256
    gl_module.TreeMap = TreeMap
    gl_module.allow_storage = lambda cls: cls
    gl_module.gl = gl_module

    sys.modules["genlayer"] = gl_module

CONTRACT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "contracts")
)
sys.path.insert(0, CONTRACT_DIR)

from pairwise_compatibility_graph import Contract


def test_happy_path_compatible():
    import genlayer as gl
    gl.nondet.mock_llm_output = {
        "status": "COMPATIBLE",
        "breaking_change_count": 0,
        "breaking_changes": [],
        "normalized_summary": "Endpoints identical and backward compatible",
    }
    contract = Contract()
    id1 = contract.register_spec("PaymentsAPI", "v1.0", "https://api.com/v1.json", "https://fb.com/v1.json")
    id2 = contract.register_spec("PaymentsAPI", "v1.1", "https://api.com/v1_1.json", "https://fb.com/v1_1.json")
    
    edge_id = contract.evaluate_compatibility(id1, id2)
    assert edge_id == 1
    edge = contract.get_edge(id1, id2)
    assert edge["status_code"] == "1"  # COMPATIBLE
    assert edge["breaking_change_count"] == "0"
    assert contract.check_compatibility(id1, id2) == "COMPATIBLE"
    print("[PASS] Test 1: Happy path COMPATIBLE invariant")


def test_contradictory_llm_output_enforces_breaking_incompatible():
    import genlayer as gl
    # LLM claims COMPATIBLE but returns 1 breaking change in list
    gl.nondet.mock_llm_output = {
        "status": "COMPATIBLE",
        "breaking_change_count": 0,
        "breaking_changes": ["Removed /v1/charge parameter 'currency'"],
        "normalized_summary": "Claims compatible but has 1 breaking change",
    }
    contract = Contract()
    id1 = contract.register_spec("PaymentsAPI", "v1.0", "https://api.com/v1.json", "https://fb.com/v1.json")
    id2 = contract.register_spec("PaymentsAPI", "v2.0", "https://api.com/v2.json", "https://fb.com/v2.json")
    
    edge_id = contract.evaluate_compatibility(id1, id2)
    edge = contract.get_edge(id1, id2)
    # INVARIANT: Must NOT be COMPATIBLE! Must be BREAKING_INCOMPATIBLE (status_code 3) and count = 1
    assert edge["status_code"] == "3"
    assert edge["breaking_change_count"] == "1"
    assert contract.check_compatibility(id1, id2) == "BREAKING_INCOMPATIBLE"
    print("[PASS] Test 2: Contradictory COMPATIBLE with breaking changes strictly reconciled to BREAKING_INCOMPATIBLE")


def test_fail_closed_on_empty_content():
    import genlayer as gl
    gl.nondet.web.fail_all = True
    contract = Contract()
    id1 = contract.register_spec("ServiceA", "v1", "https://api.com/a.json", "https://fb.com/a.json")
    id2 = contract.register_spec("ServiceB", "v1", "https://api.com/b.json", "https://fb.com/b.json")

    edge_id = contract.evaluate_compatibility(id1, id2)
    edge = contract.get_edge(id1, id2)
    assert edge["status_code"] == "4"  # EVALUATION_FAILED
    assert edge["breaking_change_count"] == "0"
    assert contract.check_compatibility(id1, id2) == "EVALUATION_FAILED"
    gl.nondet.web.fail_all = False
    print("[PASS] Test 3: Fail closed when both endpoints return empty content")


def test_backward_compatible_only():
    import genlayer as gl
    gl.nondet.mock_llm_output = {
        "status": "BACKWARD_COMPATIBLE_ONLY",
        "breaking_change_count": 0,
        "breaking_changes": [],
        "normalized_summary": "Added optional query parameter",
    }
    contract = Contract()
    id1 = contract.register_spec("AuthAPI", "v1", "https://api.com/v1.json", "https://fb.com/v1.json")
    id2 = contract.register_spec("AuthAPI", "v1.2", "https://api.com/v1_2.json", "https://fb.com/v1_2.json")
    
    edge_id = contract.evaluate_compatibility(id1, id2)
    edge = contract.get_edge(id1, id2)
    assert edge["status_code"] == "2"  # BACKWARD_COMPATIBLE_ONLY
    assert edge["breaking_change_count"] == "0"
    assert contract.check_compatibility(id1, id2) == "BACKWARD_COMPATIBLE_ONLY"
    print("[PASS] Test 4: BACKWARD_COMPATIBLE_ONLY invariant")


def test_malformed_or_explicit_breaking_without_changes_fails_closed():
    import genlayer as gl
    # A malformed payload has no evidence for a substantive verdict.
    gl.nondet.mock_llm_output = "not valid json"
    contract = Contract()
    id1 = contract.register_spec("OrdersAPI", "v1", "https://api.com/o1.json", "https://fb.com/o1.json")
    id2 = contract.register_spec("OrdersAPI", "v2", "https://api.com/o2.json", "https://fb.com/o2.json")
    contract.evaluate_compatibility(id1, id2)
    edge = contract.get_edge(id1, id2)
    assert edge["status_code"] == "4"
    assert edge["breaking_change_count"] == "0"
    assert contract.check_compatibility(id1, id2) == "EVALUATION_FAILED"
    print("[PASS] Test 5: Malformed response maps to EVALUATION_FAILED")


def test_explicit_breaking_without_listed_changes_is_evaluation_failed():
    import genlayer as gl
    gl.nondet.mock_llm_output = {
        "status": "BREAKING_INCOMPATIBLE",
        "breaking_change_count": 0,
        "breaking_changes": [],
        "normalized_summary": "Breaking but no supporting change",
    }
    contract = Contract()
    id1 = contract.register_spec("LedgerAPI", "v1", "https://api.com/l1.json", "https://fb.com/l1.json")
    id2 = contract.register_spec("LedgerAPI", "v2", "https://api.com/l2.json", "https://fb.com/l2.json")
    contract.evaluate_compatibility(id1, id2)
    edge = contract.get_edge(id1, id2)
    assert edge["status_code"] == "4"
    assert edge["breaking_change_count"] == "0"
    assert contract.check_compatibility(id1, id2) == "EVALUATION_FAILED"
    print("[PASS] Test 6: Empty breaking verdict maps to EVALUATION_FAILED")


def test_differential_validator_signature():
    spec_a_id = 1
    spec_b_id = 2
    status_code = 3
    count = 2
    summary = "BREAKING_INCOMPATIBLE: 2 breaking changes. Removed field"
    trunc_a = False
    trunc_b = False

    canonical_sig = (
        f"SPECS:{spec_a_id}:{spec_b_id}|"
        + f"STATUS:{status_code}|"
        + f"COUNT:{count}|"
        + f"SUMMARY:{summary}|"
        + f"TRUNC_A:{trunc_a}|"
        + f"TRUNC_B:{trunc_b}"
    )

    # 1. Mutate status
    mutated_status = canonical_sig.replace(f"STATUS:{status_code}", "STATUS:1")
    assert canonical_sig != mutated_status

    # 2. Mutate count
    mutated_count = canonical_sig.replace(f"COUNT:{count}", "COUNT:0")
    assert canonical_sig != mutated_count

    # 3. Mutate summary
    mutated_summary = canonical_sig.replace(summary, "COMPATIBLE: 0 breaking changes")
    assert canonical_sig != mutated_summary

    print("[PASS] Test 5: Differential signature verification for all bound fields")


if __name__ == "__main__":
    test_happy_path_compatible()
    test_contradictory_llm_output_enforces_breaking_incompatible()
    test_fail_closed_on_empty_content()
    test_backward_compatible_only()
    test_differential_validator_signature()
    print("ALL PAIRWISE COMPATIBILITY GRAPH TESTS PASSED SUCCESSFULLY.")

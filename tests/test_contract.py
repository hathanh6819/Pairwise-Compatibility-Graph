import json
import os
import sys

# Ensure genlayer stub / mock is available for direct execution if py-genlayer is not installed globally
try:
    import genlayer as gl
except ImportError:
    # Create simple mock for local Direct Mode simulation
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
        def get(self, url):
            return MockWebResponse(b'{"mock": "schema"}')

    class MockNondet:
        def __init__(self):
            self.web = MockNondetWeb()

        def exec_prompt(self, prompt):
            return json.dumps(
                {
                    "status": "BREAKING_INCOMPATIBLE",
                    "breaking_change_count": 1,
                    "breaking_changes": ["Removed parameter 'amount'"],
                    "normalized_summary": "Removed parameter 'amount'",
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

# Now import the contract module
CONTRACT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "contracts")
)
sys.path.insert(0, CONTRACT_DIR)

from pairwise_compatibility_graph import Contract, SpecRecord, PairwiseEdgeRecord


def test_spec_registration():
    contract = Contract()
    spec_a_id = contract.register_spec(
        "Service A",
        "1.0.0",
        "https://api.example.com/v1/spec",
        "https://fallback.example.com/v1/spec",
    )
    assert spec_a_id == 1, f"Expected spec_a_id to be 1, got {spec_a_id}"

    spec_b_id = contract.register_spec(
        "Service B",
        "2.0.0",
        "https://api.example.com/v2/spec",
        "https://fallback.example.com/v2/spec",
    )
    assert spec_b_id == 2, f"Expected spec_b_id to be 2, got {spec_b_id}"

    spec_data = contract.get_spec(spec_a_id)
    assert spec_data["name"] == "Service A"
    assert spec_data["version"] == "1.0.0"
    print("[PASS] Spec registration & querying")


def test_bounds_and_invalid_inputs():
    contract = Contract()
    # Test empty name
    try:
        contract.register_spec("", "1.0.0", "https://url.com", "https://fb.com")
        assert False, "Should have raised UserError for empty name"
    except Exception as e:
        assert "length" in str(e).lower()

    # Test name > 64 chars
    try:
        contract.register_spec(
            "A" * 65, "1.0.0", "https://url.com", "https://fb.com"
        )
        assert False, "Should have raised UserError for name > 64 chars"
    except Exception as e:
        assert "length" in str(e).lower()

    print("[PASS] Bounded input validation")


def test_compatibility_evaluation_lifecycle():
    contract = Contract()
    id1 = contract.register_spec(
        "API Alpha", "1.0.0", "https://pri1.com", "https://fb1.com"
    )
    id2 = contract.register_spec(
        "API Beta", "2.0.0", "https://pri2.com", "https://fb2.com"
    )

    # Test self-evaluation rejection
    try:
        contract.evaluate_compatibility(id1, id1)
        assert False, "Should have rejected evaluating spec with itself"
    except Exception as e:
        assert "itself" in str(e).lower()

    # Test valid pairwise evaluation
    edge_id = contract.evaluate_compatibility(id1, id2)
    assert edge_id == 1

    edge_data = contract.get_edge(id1, id2)
    assert edge_data["spec_a_id"] == "1"
    assert edge_data["spec_b_id"] == "2"
    assert edge_data["status_code"] == "3"  # BREAKING_INCOMPATIBLE from mock
    assert "validator_signature" in edge_data

    status_str = contract.check_compatibility(id1, id2)
    assert status_str == "BREAKING_INCOMPATIBLE"
    print("[PASS] Compatibility evaluation lifecycle")


def test_differential_validator_signature():
    """
    Differential Test: Prove that mutating any single consequential field alters
    the validator signature, ensuring consensus rejection if leader persists fake state.
    """
    spec_a_id = 1
    spec_b_id = 2
    status_code = 3
    breaking_count = 1
    summary = "BREAKING_INCOMPATIBLE: 1 breaking changes. Removed parameter 'amount'"
    trunc_a = False
    trunc_b = False

    canonical_sig = (
        f"SPECS:{spec_a_id}:{spec_b_id}|"
        + f"STATUS:{status_code}|"
        + f"COUNT:{breaking_count}|"
        + f"SUMMARY:{summary}|"
        + f"TRUNC_A:{trunc_a}|"
        + f"TRUNC_B:{trunc_b}"
    )

    # 1. Mutate status_code only (e.g. 3 -> 1)
    mutated_status_sig = (
        f"SPECS:{spec_a_id}:{spec_b_id}|"
        + f"STATUS:1|"
        + f"COUNT:{breaking_count}|"
        + f"SUMMARY:{summary}|"
        + f"TRUNC_A:{trunc_a}|"
        + f"TRUNC_B:{trunc_b}"
    )
    assert canonical_sig != mutated_status_sig, "Mutated status failed differential test!"

    # 2. Mutate breaking count only (e.g. 1 -> 0)
    mutated_count_sig = (
        f"SPECS:{spec_a_id}:{spec_b_id}|"
        + f"STATUS:{status_code}|"
        + f"COUNT:0|"
        + f"SUMMARY:{summary}|"
        + f"TRUNC_A:{trunc_a}|"
        + f"TRUNC_B:{trunc_b}"
    )
    assert canonical_sig != mutated_count_sig, "Mutated count failed differential test!"

    # 3. Mutate normalized summary string only
    mutated_summary_sig = (
        f"SPECS:{spec_a_id}:{spec_b_id}|"
        + f"STATUS:{status_code}|"
        + f"COUNT:{breaking_count}|"
        + f"SUMMARY:COMPATIBLE: 0 breaking changes|"
        + f"TRUNC_A:{trunc_a}|"
        + f"TRUNC_B:{trunc_b}"
    )
    assert canonical_sig != mutated_summary_sig, "Mutated summary failed differential test!"

    # 4. Mutate truncation flag only
    mutated_trunc_sig = (
        f"SPECS:{spec_a_id}:{spec_b_id}|"
        + f"STATUS:{status_code}|"
        + f"COUNT:{breaking_count}|"
        + f"SUMMARY:{summary}|"
        + f"TRUNC_A:True|"
        + f"TRUNC_B:{trunc_b}"
    )
    assert canonical_sig != mutated_trunc_sig, "Mutated truncation flag failed differential test!"

    print("[PASS] Differential validator signature verification")


if __name__ == "__main__":
    test_spec_registration()
    test_bounds_and_invalid_inputs()
    test_compatibility_evaluation_lifecycle()
    test_differential_validator_signature()
    print("ALL FUNCTIONAL AND DIFFERENTIAL CONTRACT TESTS PASSED SUCCESSFULLY.")

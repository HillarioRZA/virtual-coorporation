"""
Unit Tests untuk State Container dan Skema Kontrak Pydantic.
Menguji serialisasi, validasi skema ketat, dan penanganan kesalahan.
"""

import pytest
from app.engine.schemas.schemas import (
    BusinessBriefSchema,
    ComponentSpec,
    PRDContractSchema,
    QualityGateScorecard,
    SystemArchitectureSchema,
    UIComponentSpecSchema,
    UserStory,
)
from app.engine.runtime.state import VentureState


def test_business_brief_schema_valid() -> None:
    """Menguji instansiasi BusinessBriefSchema dengan data valid."""
    brief = BusinessBriefSchema(
        problem_statement="UMKM kesulitan mencatat inventaris secara akurat.",
        proposed_solution="Aplikasi POS cerdas berbasis web.",
        target_audience="Pemilik toko ritel UMKM.",
        monetization_model="flat_monthly",
        pricing_tiers=[{"tier": "Basic", "price": 99000}],
        projected_margin_percentage=65.5,
        market_feasibility_score=88,
        risks_and_mitigations=["Kompetisi tinggi: Diferensiasi melalui fitur offline-first."],
    )
    assert brief.market_feasibility_score == 88
    assert brief.projected_margin_percentage == 65.5


def test_prd_and_ui_schemas_valid() -> None:
    """Menguji instansiasi PRDContractSchema dan UIComponentSpecSchema."""
    user_story = UserStory(
        role="Admin",
        action="Upload katalog barang",
        benefit="Barang langsung tercatat di inventaris",
        acceptance_criteria=["Mendukung CSV", "Validasi kolom otomatis"],
    )
    prd = PRDContractSchema(
        product_name="Inventra POS",
        tagline="Inventaris Rapi, Bisnis Terkendali",
        core_happy_path_steps=["Daftar Akun", "Upload Produk", "Transaksi Kasir"],
        in_scope_mvp_features=[user_story],
        out_of_scope_features=["Integrasi Marketplace Multi-toko"],
    )
    assert len(prd.core_happy_path_steps) == 3

    comp = ComponentSpec(
        name="PrimaryButton",
        type="button",
        props={"variant": "primary"},
        tailwind_classes="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded",
    )
    ui_spec = UIComponentSpecSchema(
        theme_colors={"primary": "#2563eb", "background": "#f8fafc"},
        layout_type="split_screen",
        screens=["Dashboard", "Inventory", "POS"],
        components=[comp],
    )
    assert ui_spec.components[0].name == "PrimaryButton"


def test_venture_state_serialization_and_methods() -> None:
    """Menguji method serialisasi to_dict, from_dict, dan audit pada VentureState."""
    state = VentureState(
        project_id="proj_test_001",
        project_name="Inventra POS",
        founder_idea="Sistem POS untuk UMKM",
        selected_archetype=1,
    )

    # Uji pencatatan event & token cost
    state.record_event("Inisialisasi sparring room.")
    state.add_token_cost("COS", 0.042)
    state.add_token_cost("COS", 0.018)

    assert len(state.event_logs) == 1
    assert state.token_usage["COS"] == 0.06

    # Uji serialisasi
    data_dict = state.to_dict()
    assert data_dict["project_id"] == "proj_test_001"
    assert data_dict["token_usage"]["COS"] == 0.06

    # Uji deserialisasi
    restored_state = VentureState.from_dict(data_dict)
    assert restored_state.project_id == state.project_id
    assert restored_state.token_usage["COS"] == 0.06


def test_venture_state_invalid_data_raises_value_error() -> None:
    """Menguji bahwa input data salah pada from_dict melempar ValueError."""
    with pytest.raises(ValueError) as exc_info:
        VentureState.from_dict({"project_id": 12345})  # Missing required fields
    assert "Invalid VentureState data" in str(exc_info.value)

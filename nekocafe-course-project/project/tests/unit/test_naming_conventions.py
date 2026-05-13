from libs.common.naming import ID_PREFIXES, PRIMARY_BOUNDED_CONTEXTS


def test_id_prefixes_cover_cross_lab_shared_baseline():
    assert ID_PREFIXES == {
        "functional_requirement": "FR",
        "non_functional_requirement": "NFR",
        "use_case": "UC",
        "bounded_context": "BC",
        "service": "SVC",
        "test_case": "TC",
    }


def test_primary_bounded_contexts_keep_two_services_runnable_and_four_design_only():
    assert PRIMARY_BOUNDED_CONTEXTS == [
        "BC-MEMBER",
        "BC-RESERVATION",
        "BC-ORDER",
        "BC-STORE-OPS",
        "BC-CAT-HEALTH",
        "BC-RECOMMENDATION",
    ]

"""Tests for Aldes telemetry indexes and command codes."""


def test_air_modes_map_all_uam_indexes_to_apk_codes(const_module):
    assert {index for index, _ in const_module.AIR_MODES.values()} == set(range(9))
    assert [code for _, code in const_module.AIR_MODES.values()] == list("ABCDEFGHI")


def test_water_modes_map_all_udm_indexes_to_apk_codes(const_module):
    assert {index for index, _ in const_module.WATER_MODES.values()} == {0, 1, 2}
    assert [code for _, code in const_module.WATER_MODES.values()] == list("LMN")

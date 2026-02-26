"""Test myenergi sensor."""

from unittest.mock import MagicMock

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from . import setup_mock_myenergi_config_entry

TEST_ZAPPI_SELECT_CHARGE_MODE = "select.myenergi_test_zappi_1_charge_mode"
TEST_EDDI_SELECT_OP_MODE = "select.myenergi_test_eddi_1_operating_mode"


async def test_boost(hass: HomeAssistant, mock_zappi_start_boost: MagicMock) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    assert mock_zappi_start_boost.call_count == 0
    await hass.services.async_call(
        "myenergi",
        "myenergi_boost",
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_SELECT_CHARGE_MODE,
            "amount": "44",
        },
        blocking=False,
    )
    await hass.async_block_till_done()
    assert mock_zappi_start_boost.call_count == 1
    mock_zappi_start_boost.assert_called_with(44.0)


async def test_smart_boost(
    hass: HomeAssistant, mock_zappi_start_smart_boost: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    assert mock_zappi_start_smart_boost.call_count == 0
    await hass.services.async_call(
        "myenergi",
        "myenergi_smart_boost",
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_SELECT_CHARGE_MODE,
            "amount": "11",
            "when": "12:13:14",
        },
        blocking=False,
    )
    await hass.async_block_till_done()
    assert mock_zappi_start_smart_boost.call_count == 1
    mock_zappi_start_smart_boost.assert_called_with(11.0, "1213")


async def test_eddi_boost(
    hass: HomeAssistant, mock_eddi_manual_boost: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    assert mock_eddi_manual_boost.call_count == 0
    await hass.services.async_call(
        "myenergi",
        "myenergi_eddi_boost",
        {ATTR_ENTITY_ID: TEST_EDDI_SELECT_OP_MODE, "target": "Heater 1", "time": 44},
        blocking=False,
    )
    await hass.async_block_till_done()
    assert mock_eddi_manual_boost.call_count == 1
    mock_eddi_manual_boost.assert_called_with("Heater 1", 44.0)


async def test_stop_boost(
    hass: HomeAssistant, mock_zappi_stop_boost: MagicMock
) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    assert mock_zappi_stop_boost.call_count == 0
    await hass.services.async_call(
        "myenergi",
        "myenergi_stop_boost",
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_SELECT_CHARGE_MODE,
        },
        blocking=False,
    )
    await hass.async_block_till_done()
    assert mock_zappi_stop_boost.call_count == 1


async def test_unlock(hass: HomeAssistant, mock_zappi_unlock: MagicMock) -> None:
    """Verify device information includes expected details."""

    await setup_mock_myenergi_config_entry(hass)

    assert mock_zappi_unlock.call_count == 0
    await hass.services.async_call(
        "myenergi",
        "myenergi_unlock",
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_SELECT_CHARGE_MODE,
        },
        blocking=False,
    )
    await hass.async_block_till_done()
    assert mock_zappi_unlock.call_count == 1


async def test_set_managed_mode(
    hass: HomeAssistant, mock_set_managed_mode: MagicMock
) -> None:
    """Verify managed mode service call."""

    await setup_mock_myenergi_config_entry(hass)

    assert mock_set_managed_mode.call_count == 0
    await hass.services.async_call(
        "myenergi",
        "myenergi_set_managed_mode",
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_SELECT_CHARGE_MODE,
            "managed_mode_enabled": True,
            "auto_scheduler_enabled": False,
        },
        blocking=False,
    )
    await hass.async_block_till_done()
    assert mock_set_managed_mode.call_count == 1
    mock_set_managed_mode.assert_called_with(True, False)


async def test_set_super_schedule_slot(
    hass: HomeAssistant, mock_set_super_schedule_slot: MagicMock
) -> None:
    """Verify super schedule slot service call."""

    await setup_mock_myenergi_config_entry(hass)

    assert mock_set_super_schedule_slot.call_count == 0
    await hass.services.async_call(
        "myenergi",
        "myenergi_set_super_schedule_slot",
        {
            ATTR_ENTITY_ID: TEST_ZAPPI_SELECT_CHARGE_MODE,
            "start_time": "2026-01-15T22:00:00.000Z",
            "end_time": "2026-01-16T06:00:00.000Z",
            "mode": "MODE_ECO_PLUS",
            "charge_rate_watts": 3500,
            "energy_target_wh": 10000,
        },
        blocking=False,
    )
    await hass.async_block_till_done()
    assert mock_set_super_schedule_slot.call_count == 1
    mock_set_super_schedule_slot.assert_called_with(
        "2026-01-15T22:00:00.000Z",
        "2026-01-16T06:00:00.000Z",
        "MODE_ECO_PLUS",
        3500.0,
        10000.0,
    )

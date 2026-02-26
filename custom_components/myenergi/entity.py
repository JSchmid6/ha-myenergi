"""MyenergiEntity class"""

import logging
from typing import Any

from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


class MyenergiEntity(CoordinatorEntity):
    def __init__(self, coordinator, device, config_entry, meta=None):
        super().__init__(coordinator)
        self.device = device
        self.coordinator = coordinator
        self.config_entry = config_entry
        if meta is None:
            self.meta = {"attrs": {}}
        else:
            self.meta = meta
            if self.meta.get("category", None) is not None:
                self.meta["category"] = EntityCategory(self.meta["category"])

    #    async def async_added_to_hass(self):
    #        """Run when about to be added to hass."""
    #        async_dispatcher_connect(
    #            # The Hass Object
    #            self.hass,
    #            # The Signal to listen for.
    #            # Try to make it unique per entity instance
    #            # so include something like entity_id
    #            # or other unique data from the service call
    #            self.entity_id,
    #            # Function handle to call when signal is received
    #            self.libbi_set_charge_target
    #        )
    #        _LOGGER.debug("registered signal with HA")
    #
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device.serial_number)},
            "name": self.device.name,
            "model": self.device.kind.capitalize(),
            "manufacturer": "myenergi",
            "sw_version": self.device.firmware_version,
        }

    @property
    def entity_category(self):
        return self.meta.get("category", None)

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            "integration": DOMAIN,
        }
        return {**attrs, **self.meta["attrs"]}

    async def start_boost(self, amount: float) -> None:
        _LOGGER.debug("Start boost called, amount %s", amount)
        """Start boost"""
        await self.device.start_boost(amount)
        self.schedule_update_ha_state()

    async def start_eddi_boost(self, target: str, time: float) -> None:
        _LOGGER.debug("Start eddi boost called, time %s target %s", time, target)
        """Start eddi boost"""
        await self.device.manual_boost(target, time)
        self.schedule_update_ha_state()

    async def start_smart_boost(self, amount: float, when: str) -> None:
        _LOGGER.debug("Start smart boost called, amount %s when %s", amount, when)
        """Start boost"""
        when = when.replace(":", "")[:4]
        await self.device.start_smart_boost(amount, when)
        self.schedule_update_ha_state()

    async def stop_boost(self) -> None:
        _LOGGER.debug("Stop boost called")
        """Stop boost"""
        await self.device.stop_boost()
        self.schedule_update_ha_state()

    async def unlock(self) -> None:
        _LOGGER.debug("unlock called")
        """Unlock"""
        await self.device.unlock()

    async def libbi_set_charge_target(self, chargetarget: float) -> None:
        _LOGGER.debug("Setting libbi charge target to %s Wh", chargetarget)
        """Set libbi charge target"""
        await self.device.set_charge_target(chargetarget)
        self.schedule_update_ha_state()

    async def _call_s18_api(
        self,
        method: str,
        endpoint: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        connection = self.coordinator.client._connection
        if not connection.app_email or not connection.app_password:
            raise ValueError(
                "App credentials are required for this service. "
                "Please configure app_email and app_password in integration options."
            )

        await self.hass.async_add_executor_job(connection.checkAndUpdateToken)
        headers = {"Authorization": f"Bearer {connection.oauth.access_token}"}
        response = await connection.asyncClient.request(
            method,
            f"https://api.s18.myenergi.net{endpoint}",
            json=payload,
            headers=headers,
            timeout=connection.timeout,
        )
        response.raise_for_status()
        if response.content:
            return response.json()
        return {}

    @property
    def _s18_device_id(self) -> str:
        if self.device.kind == "zappi":
            return f"ZA{self.device.serial_number}"
        raise ValueError(f"Unsupported device kind for s18 API: {self.device.kind}")

    async def set_managed_mode(
        self,
        managed_mode_enabled: bool,
        auto_scheduler_enabled: bool | None = None,
    ) -> None:
        payload: dict[str, Any] = {"managedModeEnabled": managed_mode_enabled}
        if auto_scheduler_enabled is not None:
            payload["autoSchedulerEnabled"] = auto_scheduler_enabled
        await self._call_s18_api(
            "PATCH",
            f"/devices/{self._s18_device_id}/cloud-configuration",
            payload,
        )
        self.schedule_update_ha_state()

    async def set_super_schedule_slot(
        self,
        start_time: str,
        end_time: str,
        mode: str,
        charge_rate_watts: float | None = None,
        energy_target_wh: float | None = None,
    ) -> None:
        slot: dict[str, Any] = {
            "startTime": start_time,
            "endTime": end_time,
            "mode": mode,
        }
        if charge_rate_watts is not None:
            slot["chargeRateWatts"] = int(charge_rate_watts)
        if energy_target_wh is not None:
            slot["energyTargetWh"] = int(energy_target_wh)

        await self._call_s18_api(
            "PUT",
            f"/devices/{self._s18_device_id}/super-schedule",
            {"chargeSchedules": [slot]},
        )
        self.schedule_update_ha_state()


class MyenergiHub(CoordinatorEntity):
    def __init__(self, coordinator, config_entry, meta):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.coordinator = coordinator
        self.meta = meta
        if meta is not None:
            if self.meta.get("category", None) is not None:
                self.meta["category"] = EntityCategory(self.meta["category"])

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.client.serial_number)},
            "name": self.coordinator.client.site_name,
            "model": "Hub",
            "manufacturer": "myenergi",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            "integration": DOMAIN,
        }
        return {**attrs, **self.meta["attrs"]}

    @property
    def entity_category(self):
        return self.meta.get("category", None)

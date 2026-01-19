from __future__ import annotations
"""The Heating Controller integration"""
"""Author: Jozef Moravcik"""
"""email: jozef.moravcik@moravcik.eu"""

""" switch.py """

"""Switch platform for Heating Controller integration."""

import logging
from typing import Any
from datetime import timedelta

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.entity import EntityCategory, DeviceInfo

from .const import *

LOGGER = logging.getLogger(__name__)

async def _load_translations(hass: HomeAssistant) -> dict:
    """Load translations for the current language."""
    import json
    import os
    
    def _load_file():
        try:
            language = hass.config.language if hass else "en"
            
            # Skúsiť načítať translations súbor pre daný jazyk
            translations_path = os.path.join(os.path.dirname(__file__), "translations", f"{language}.json")
            
            # Ak neexistuje pre daný jazyk, použiť strings.json ako fallback
            if not os.path.exists(translations_path):
                translations_path = os.path.join(os.path.dirname(__file__), "strings.json")
            
            if os.path.exists(translations_path):
                with open(translations_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    return await hass.async_add_executor_job(_load_file)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Heating Controller switch entities."""
    instance = hass.data[DOMAIN][entry.entry_id]["instance"]
    
    # Načítať translations asynchrónne
    translations = await _load_translations(hass)

    entities = [
        SwitchEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_AUTOMATIC_MODE,
            name = "Automatic mode",
            translations = translations,
            icon = "mdi:auto-mode",
            icon_off = "mdi:stop-circle-outline",
            initial_state = True,
            restore_state = True,
            device_class = SwitchDeviceClass.SWITCH,
        ),
        SwitchEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_ACC1_ENABLE,
            name = "ACC 1 - ON/OFF",
            translations = translations,
            icon = "mdi:numeric-1-box",
            icon_off = "mdi:numeric-1-box-outline",
            initial_state = True,
            restore_state = True,
            device_class = SwitchDeviceClass.SWITCH,
        ),
        SwitchEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_ACC2_ENABLE,
            name = "ACC 2 - ON/OFF",
            translations = translations,
            icon = "mdi:numeric-2-box",
            icon_off="mdi:numeric-2-box-outline",
            initial_state = True,
            restore_state = True,
            device_class = SwitchDeviceClass.SWITCH,
        ),
        SwitchEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_HP_ACC,
            name = "TC to ACC",
            translations = translations,
            icon = "mdi:transfer-right",
            icon_off = "mdi:stop-circle-outline",
            initial_state = True,
            restore_state = True,
            device_class = SwitchDeviceClass.SWITCH,
        ),
        SwitchEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_HP_DHW,
            name = "TC to DHW",
            translations = translations,
            icon = "mdi:transfer-right",
            icon_off = "mdi:stop-circle-outline",
            initial_state = False,
            restore_state = True,
            device_class = SwitchDeviceClass.SWITCH,
        ),
        SwitchEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_HEAT_DHW_FROM_ACC,
            name = "Heat DHW from ACC",
            translations = translations,
            icon = "mdi:transfer",
            icon_off = "mdi:transfer",
            initial_state = False,
            restore_state = False,
            device_class = SwitchDeviceClass.SWITCH,
        ),
        SwitchEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_HEATING_SOURCE_ON_OFF,
            name = "Heating source ON/OFF",
            translations = translations,
            icon = "mdi:hvac",
            icon_off="mdi:hvac-off",
            initial_state = True,
            restore_state = True,
            device_class = SwitchDeviceClass.SWITCH,
        ),
    ]

    # Uložím switche do dictionary pre vzájomné prepínanie
    switches_dict = {entity._entity_id: entity for entity in entities}
    hass.data[DOMAIN][entry.entry_id]["switches"] = switches_dict

    async_add_entities(entities)


class SwitchEntityDefinition(SwitchEntity, RestoreEntity):

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name=NAME,
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version=VERSION,
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            "integration": DOMAIN,
            "entry_id": self._entry_id,
            "entity_id": self._entity_id,
            "restore_state": self._restore_state,
        }

    def __init__(
        self,
        instance,
        entry_id: str,
        entity_id: str,
        name: str,
        translations: dict = None,
        icon: str = "mdi:toggle-switch-variant",
        icon_off: str | None = None,
        initial_state: bool = False,
        enabled_by_default: bool = True,
        restore_state: bool = True,
        device_class: SwitchDeviceClass | None = None,
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Initialize the switch."""
        self._instance = instance
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_{entity_id}"
        self._attr_has_entity_name = False
        self._attr_translation_key = entity_id

        # Načítať názov z preloaded translations
        if translations:
            entity_trans = translations.get("entity", {}).get("switch", {}).get(entity_id, {})
            translated_name = entity_trans.get("name")
            if translated_name:
                self._attr_name = translated_name
            else:
                self._attr_name = name
        else:
            self._attr_name = name
        
        self.entity_id = f"switch.{DOMAIN}_{entity_id}"
        self._icon_on = icon
        self._icon_off = icon_off if icon_off else icon
        self._entity_id = entity_id
        self._initial_state = initial_state
        self._attr_is_on = initial_state
        self._restore_state = restore_state
        self._attr_entity_registry_enabled_default = enabled_by_default
        self._attr_entity_registry_visible_default = enabled_by_default
        if device_class is not None:
            self._attr_device_class = device_class
        if entity_category is not None:
            self._attr_entity_category = entity_category
        self._hass = None
        self._timer_cancel = None
        self._restore_state = restore_state
    
    @property
    def icon(self):
        """Return the icon based on current state."""
        return self._icon_on if self._attr_is_on else self._icon_off

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        self._hass = self.hass
        
        # Obnovenie stavu po reštarte (len ak je restore_state povolené)
        if self._restore_state:
            last_state = await self.async_get_last_state()
            if last_state is not None:
                self._attr_is_on = last_state.state == "on"
                LOGGER.debug(f"Restored state for {self.entity_id}: {self._attr_is_on}")
            else:
                # Ak nemáme uložený stav, použijeme initial_state
                self._attr_is_on = self._initial_state
                LOGGER.debug(f"No saved state for {self.entity_id}, using initial: {self._attr_is_on}")
        
        # Subscribe to updates
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_feedback_update_{self._entry_id}",
                self._handle_feedback_update,
            )
        )

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        await super().async_will_remove_from_hass()
        
        # Zrušiť časovač ak existuje
        if self._timer_cancel:
            self._timer_cancel()
            self._timer_cancel = None

    @callback
    def _handle_feedback_update(self) -> None:
        """Handle feedback update."""
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        # Vzájomné vylučovanie TC_ACC a TC_DHW
        if self._entity_id == ENTITY_HP_ACC:
            # Ak zapíname TC_ACC, musíme vypnúť TC_DHW
            await self._toggle_exclusive_switch(ENTITY_HP_DHW, False)
        elif self._entity_id == ENTITY_HP_DHW:
            # Ak zapíname TC_DHW, musíme vypnúť TC_ACC
            await self._toggle_exclusive_switch(ENTITY_HP_ACC, False)
        
        # Časovač pre heat_dhw_from_acc
        if self._entity_id == ENTITY_HEAT_DHW_FROM_ACC and self._hass:
            # Zrušiť existujúci časovač ak existuje
            if self._timer_cancel:
                self._timer_cancel()
                self._timer_cancel = None
            
            # Získať timeout z konfigurácie
            timeout_minutes = self._hass.data[DOMAIN][self._entry_id].get(CONF_TIMEOUT_HEAT_DHW, DEFAULT_TIMEOUT_HEAT_DHW)
            
            # Spustiť nový časovač
            self._timer_cancel = async_call_later(
                self._hass,
                timeout_minutes * 60,  # konverzia minút na sekundy
                self._timer_finished
            )
            LOGGER.info(f"Heat DHW from ACC timer started for {timeout_minutes} minutes")
        
        self._attr_is_on = True
        self.async_write_ha_state()
        LOGGER.debug(f"Switch {self.entity_id} turned ON")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        # Ochrana pre ACC1_ENABLE a ACC2_ENABLE - aspoň jeden musí byť zapnutý
        if self._entity_id == ENTITY_ACC1_ENABLE:
            # Kontrola stavu ACC2_ENABLE
            if not await self._check_other_acc_state(ENTITY_ACC2_ENABLE):
                # Ignoruje sa príkaz - ostane zapnutý
                self._attr_is_on = True
                self.async_write_ha_state()
                return
        elif self._entity_id == ENTITY_ACC2_ENABLE:
            # Kontrola stavu ACC1_ENABLE
            if not await self._check_other_acc_state(ENTITY_ACC1_ENABLE):
                # Ignoruje sa príkaz - ostane zapnutý
                self._attr_is_on = True
                self.async_write_ha_state()
                return
        
        # Vzájomné vylučovanie TC_ACC a TC_DHW - nesmú byť obidva vypnuté
        if self._entity_id == ENTITY_HP_ACC:
            # Ak sa vypína TC_ACC, musí sa zapnúť TC_DHW
            await self._toggle_exclusive_switch(ENTITY_HP_DHW, True)
        elif self._entity_id == ENTITY_HP_DHW:
            # Ak sa vypína TC_DHW, musí sa zapnúť TC_ACC
            await self._toggle_exclusive_switch(ENTITY_HP_ACC, True)
        
        # Zrušiť časovač pre heat_dhw_from_acc
        if self._entity_id == ENTITY_HEAT_DHW_FROM_ACC and self._timer_cancel:
            self._timer_cancel()
            self._timer_cancel = None
            LOGGER.info("Heat DHW from ACC timer cancelled")
        
        self._attr_is_on = False
        self.async_write_ha_state()
        LOGGER.debug(f"Switch {self.entity_id} turned OFF")
    
    async def _toggle_exclusive_switch(self, other_entity_id: str, target_state: bool) -> None:
        """Toggle the exclusive switch (TC_ACC or TC_DHW)."""
        if self._hass is None:
            return
        
        try:
            # Získame dictionary switchov z hass.data
            switches_dict = self._hass.data[DOMAIN][self._entry_id].get("switches", {})
            other_switch = switches_dict.get(other_entity_id)
            
            if other_switch:
                # Priamo nastavíme stav druhého switchu
                other_switch._attr_is_on = target_state
                other_switch.async_write_ha_state()
                LOGGER.debug(f"Set {other_entity_id} to {target_state}")
            else:
                LOGGER.warning(f"Switch {other_entity_id} not found in switches dictionary")
        except Exception as ex:
            LOGGER.error(f"Failed to toggle {other_entity_id}: {ex}")
    
    async def _check_other_acc_state(self, other_entity_id: str) -> bool:
        """Check if the other ACC switch is ON. Returns True if ON, False if OFF."""
        if self._hass is None:
            return False
        
        try:
            # Získame dictionary switchov z hass.data
            switches_dict = self._hass.data[DOMAIN][self._entry_id].get("switches", {})
            other_switch = switches_dict.get(other_entity_id)
            
            if other_switch:
                is_on = other_switch._attr_is_on
                LOGGER.debug(f"Checked {other_entity_id} state: {is_on}")
                return is_on
            else:
                LOGGER.warning(f"Switch {other_entity_id} not found in switches dictionary")
                return False
        except Exception as ex:
            LOGGER.error(f"Failed to check {other_entity_id} state: {ex}")
            return False
    
    @callback
    def _timer_finished(self, _now=None) -> None:
        """Called when heat_dhw_from_acc timer finishes."""
        LOGGER.info(f"Heat DHW from ACC timer finished - turning OFF")
        self._timer_cancel = None
        self._attr_is_on = False
        self.async_write_ha_state()
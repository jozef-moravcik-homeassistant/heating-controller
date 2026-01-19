from __future__ import annotations
"""The Heating Controller integration"""
"""Author: Jozef Moravcik"""
"""email: jozef.moravcik@moravcik.eu"""

""" sensor.py """

"""Sensor platform for Heating Controller integration."""

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory, DeviceInfo

from .const import *

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
    """Set up Heating Controller sensor entities."""
    instance = hass.data[DOMAIN][entry.entry_id]["instance"]

    # Načítať translations asynchrónne
    translations = await _load_translations(hass)

    entities = [
        SensorEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_CONTROL_COMMAND_ON_OFF,
            name = "TC - ON/OFF",
            translations = translations,
            icon = "mdi:check-circle",
            default_value = STATE_OFF,
            enabled_by_default = True,
        ),
        SensorEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_CONTROL_COMMAND_TEMPERATURE,
            name = "TC - Temperature",
            translations = translations,
            icon = "mdi:thermometer-water",
            default_value = MIN_TEMPERATURE_LIMIT,
            enabled_by_default = True,
        ),
        SensorEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_CONTROL_COMMAND_HP_ON_OFF,
            name = "TC - ON/OFF",
            translations = translations,
            icon = "mdi:check-circle",
            default_value = STATE_OFF,
            enabled_by_default = True,
        ),
        SensorEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_CONTROL_COMMAND_HP_TEMPERATURE,
            name = "TC - Temperature",
            translations = translations,
            icon = "mdi:thermometer-water",
            default_value = MIN_TEMPERATURE_LIMIT,
            enabled_by_default = True,
        ),
        SensorEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_CURRENT_OPERATING_MODE,
            name = "Current Operating mode",
            translations = translations,
            icon = "mdi:arrow-decision",
            default_value = CURRENT_OPERATING_MODE_UNDEFINED,
            enabled_by_default = True,
        ),
        SensorEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_CURRENT_OPERATING_MODE_TEXT,
            name = "Current Operating mode (text)",
            translations = translations,
            icon = "mdi:arrow-decision",
            device_class=SensorDeviceClass.ENUM,
            options=CURRENT_OPERATING_MODE_TEXT_OPTIONS,
            default_value=CURRENT_OPERATING_MODE_UNDEFINED_TEXT,
        ),
    ]

    async_add_entities(entities)

class SensorEntityDefinition(SensorEntity):

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
        }

    def __init__(
        self,
        instance,
        entry_id: str,
        entity_id: str,
        name: str,
        translations: dict = None,
        icon: str = "mdi:eye",
        default_value: str = None,
        enabled_by_default: bool = True,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        native_unit_of_measurement: str | None = None,
        suggested_display_precision: int | None = None,
        suggested_unit_of_measurement: str | None = None,
        entity_category: EntityCategory | None = None,
        options: list[str] | None = None,
        available: bool = True,
        last_reset: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        self._instance = instance
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_{entity_id}"
        self._attr_has_entity_name = False
        self._attr_translation_key = entity_id
        
        # Načítať názov z preloaded translations
        if translations:
            entity_trans = translations.get("entity", {}).get("sensor", {}).get(entity_id, {})
            translated_name = entity_trans.get("name")
            if translated_name:
                self._attr_name = translated_name
            else:
                self._attr_name = name
        else:
            self._attr_name = name
        
        self.entity_id = f"sensor.{DOMAIN}_{entity_id}"
        self._attr_icon = icon
        self._entity_id = entity_id
        self._attr_native_value = default_value
        self._attr_available = available
        self._attr_entity_registry_enabled_default = enabled_by_default
        self._attr_entity_registry_visible_default = enabled_by_default
        
        if device_class is not None:
            self._attr_device_class = device_class
        if state_class is not None:
            self._attr_state_class = state_class
        if native_unit_of_measurement is not None:
            self._attr_native_unit_of_measurement = native_unit_of_measurement
        if suggested_display_precision is not None:
            self._attr_suggested_display_precision = suggested_display_precision
        if suggested_unit_of_measurement is not None:
            self._attr_suggested_unit_of_measurement = suggested_unit_of_measurement
        if entity_category is not None:
            self._attr_entity_category = entity_category
        if options is not None:
            self._attr_options = options
        if last_reset is not None:
            self._attr_last_reset = last_reset

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Subscribe to updates
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_feedback_update_{self._entry_id}",
                self._handle_feedback_update,
            )
        )

    @callback
    def _handle_feedback_update(self) -> None:
        """Handle feedback update."""
        new_value = self._instance.sensor_states.get(self._entity_id)
        if new_value is not None:
            self._attr_native_value = new_value
        self.async_write_ha_state()

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return self._attr_native_value
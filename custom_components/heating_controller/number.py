from __future__ import annotations
"""The Heating Controller integration"""
"""Author: Jozef Moravcik"""
"""email: jozef.moravcik@moravcik.eu"""

""" number.py """

"""Number platform for Heating Controller integration."""

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode, NumberDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.entity import EntityCategory, DeviceInfo

from .const import (
    DOMAIN,
    NAME,
    VERSION,
    MANUFACTURER,
    MODEL,
    ENTITY_DHW_TARGET_TEMPERATURE,
    ENTITY_ACC_TARGET_TEMPERATURE,
    DEFAULT_DHW_TARGET_TEMPERATURE,
    DEFAULT_ACC_TARGET_TEMPERATURE,
    MIN_TEMPERATURE_LIMIT,
    MAX_TEMPERATURE_LIMIT
)


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


def _coerce_value(value: float, step: float) -> int | float:
    """Ak je krok celé číslo, vráť int aby HA nezobrazoval desatinné miesto."""
    if value is None:
        return value
    if step == int(step):
        return int(value)
    return value


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Heating Controller number entities."""
    instance = hass.data[DOMAIN][entry.entry_id]["instance"]

    # Načítať translations asynchrónne
    translations = await _load_translations(hass)

    entities = [
        NumberEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_DHW_TARGET_TEMPERATURE,
            name = "DHW target temperature",
            translations = translations,
            icon = "mdi:thermometer-water",
            min_value = MIN_TEMPERATURE_LIMIT,
            max_value = MAX_TEMPERATURE_LIMIT,
            step = 1.0,
            default_value = DEFAULT_DHW_TARGET_TEMPERATURE,
            enabled_by_default = True,
            mode = NumberMode.BOX,
            native_unit_of_measurement = "°C",
        ),
        NumberEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_ACC_TARGET_TEMPERATURE,
            name = "ACC target temperature",
            translations = translations,
            icon = "mdi:thermometer",
            min_value = MIN_TEMPERATURE_LIMIT,
            max_value = MAX_TEMPERATURE_LIMIT,
            step = 1.0,
            default_value = DEFAULT_ACC_TARGET_TEMPERATURE,
            enabled_by_default = True,
            mode = NumberMode.BOX,
            native_unit_of_measurement = "°C",
        ),
    ]

    # Uložím number entity do dictionary
    numbers_dict = {entity._entity_id: entity for entity in entities}
    hass.data[DOMAIN][entry.entry_id]["numbers"] = numbers_dict

    async_add_entities(entities)

class NumberEntityDefinition(NumberEntity, RestoreEntity):

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
            "min_value": self._attr_native_min_value,
            "max_value": self._attr_native_max_value,
            "step": self._attr_native_step,
        }

    def __init__(
        self,
        instance,
        entry_id: str,
        entity_id: str,
        name: str,
        translations: dict = None,
        icon: str = "mdi:numeric",
        min_value: float = 0,
        max_value: float = 1,
        step: float = 1,
        default_value: float = None,
        enabled_by_default: bool = True,
        mode: NumberMode = NumberMode.SLIDER,
        native_unit_of_measurement: str | None = None,
        device_class: NumberDeviceClass | None = None,
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Initialize the number entity."""
        self._instance = instance
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_{entity_id}"
        self._attr_has_entity_name = False
        self._attr_translation_key = entity_id
        
        # Načítať názov z preloaded translations
        if translations:
            entity_trans = translations.get("entity", {}).get("number", {}).get(entity_id, {})
            translated_name = entity_trans.get("name")
            if translated_name:
                self._attr_name = translated_name
            else:
                self._attr_name = name
        else:
            self._attr_name = name
        
        self.entity_id = f"number.{DOMAIN}_{entity_id}"
        self._attr_icon = icon
        self._entity_id = entity_id
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_mode = mode
        self._default_value = default_value
        # Uložiť ako int ak je krok celé číslo → HA nezobrazí desatinné miesto
        self._attr_native_value = _coerce_value(default_value, step)
        self._attr_entity_registry_enabled_default = enabled_by_default
        self._attr_entity_registry_visible_default = enabled_by_default

        if native_unit_of_measurement is not None:
            self._attr_native_unit_of_measurement = native_unit_of_measurement
        if device_class is not None:
            self._attr_device_class = device_class
        if entity_category is not None:
            self._attr_entity_category = entity_category

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()

        # Obnovenie stavu po reštarte
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state not in (None, "unknown", "unavailable"):
            try:
                restored = float(last_state.state)
                self._attr_native_value = _coerce_value(restored, self._attr_native_step)
                LOGGER.debug(f"Restored state for {self.entity_id}: {self._attr_native_value}")
            except (ValueError, TypeError):
                self._attr_native_value = _coerce_value(self._default_value, self._attr_native_step)
                LOGGER.debug(f"Failed to restore state for {self.entity_id}, using default: {self._default_value}")
        else:
            self._attr_native_value = _coerce_value(self._default_value, self._attr_native_step)
            LOGGER.debug(f"No saved state for {self.entity_id}, using default: {self._default_value}")

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
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set the value of the number entity."""
        self._attr_native_value = _coerce_value(value, self._attr_native_step)
        self.async_write_ha_state()
        LOGGER.debug(f"Number {self.entity_id} set to {self._attr_native_value}")
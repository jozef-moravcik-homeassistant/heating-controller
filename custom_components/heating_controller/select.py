from __future__ import annotations
"""The Heating Controller integration"""
"""Author: Jozef Moravcik"""
"""email: jozef.moravcik@moravcik.eu"""

""" select.py """

"""Select platform for Heating Controller integration"""

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
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
    ENTITY_HEATING_OPERATING_MODE,
    DEFAULT_HEATING_OPERATING_MODE,
    HEATING_OPERATING_MODE_OPTIONS,
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

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Heating Controller select entities."""
    instance = hass.data[DOMAIN][entry.entry_id]["instance"]

    # Načítať translations asynchrónne
    translations = await _load_translations(hass)

    entities = [
        SelectEntityDefinition(
            instance,
            entry_id = entry.entry_id,
            entity_id = ENTITY_HEATING_OPERATING_MODE,
            name = "Heating operating mode",
            translations = translations, 
            icon = "mdi:arrow-decision",
            options = [str(x) for x in HEATING_OPERATING_MODE_OPTIONS],
            default_value = str(DEFAULT_HEATING_OPERATING_MODE),
            enabled_by_default = True,
        ),
    ]

    # Uložím select entity do dictionary
    selects_dict = {entity._entity_id: entity for entity in entities}
    hass.data[DOMAIN][entry.entry_id]["selects"] = selects_dict

    async_add_entities(entities)

class SelectEntityDefinition(SelectEntity, RestoreEntity):

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
            "options": self._attr_options,
        }

    def __init__(
        self,
        instance,
        entry_id: str,
        entity_id: str,
        name: str,
        translations: dict = None,
        icon: str = "mdi:format-list-checkbox",
        options: list[str] = None,
        default_value: str = None,
        enabled_by_default: bool = True,
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Initialize the select entity."""
        self._instance = instance
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_{entity_id}"
        self._attr_has_entity_name = False
        self._attr_translation_key = entity_id
        
        # Načítať názov z preloaded translations
        if translations:
            entity_trans = translations.get("entity", {}).get("select", {}).get(entity_id, {})
            translated_name = entity_trans.get("name")
            if translated_name:
                self._attr_name = translated_name
            else:
                self._attr_name = name
        else:
            self._attr_name = name
        
        self.entity_id = f"select.{DOMAIN}_{entity_id}"
        self._attr_icon = icon
        self._entity_id = entity_id
        self._attr_options = options
        self._default_value = default_value
        self._attr_current_option = default_value
        self._attr_entity_registry_enabled_default = enabled_by_default
        self._attr_entity_registry_visible_default = enabled_by_default
        
        if entity_category is not None:
            self._attr_entity_category = entity_category

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()

        # Obnovenie stavu po reštarte
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state not in (None, "unknown", "unavailable"):
            if last_state.state in self._attr_options:
                self._attr_current_option = last_state.state
                LOGGER.debug(f"Restored state for {self.entity_id}: {self._attr_current_option}")
            else:
                self._attr_current_option = self._default_value
                LOGGER.debug(f"Invalid restored state for {self.entity_id}, using default: {self._default_value}")
        else:
            self._attr_current_option = self._default_value
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

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option in self._attr_options:
            self._attr_current_option = option
            self.async_write_ha_state()
            LOGGER.debug(f"Select {self.entity_id} set to {option}")
        else:
            LOGGER.warning(f"Invalid option {option} for {self.entity_id}")
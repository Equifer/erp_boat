"""Sensor platform for ERP Boat."""
import logging
from datetime import datetime, timezone
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up ERP Boat sensor based on a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]["data"]
    
    # We create a sensor for each maintenance task
    entities = []
    for task in data.get("maintenance", []):
        entities.append(MaintenanceTaskSensor(hass, entry.entry_id, task))
        
    # We create a summary sensor for Inventory
    if data.get("inventory"):
        entities.append(InventorySummarySensor(hass, entry.entry_id, data.get("inventory")))
        
    # We create a summary sensor for Documents
    if data.get("documents"):
        entities.append(DocumentSummarySensor(hass, entry.entry_id, data.get("documents")))
        
    async_add_entities(entities)


class MaintenanceTaskSensor(SensorEntity):
    """Representation of an ERP Boat Maintenance Task."""

    def __init__(self, hass: HomeAssistant, entry_id: str, task: dict) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._entry_id = entry_id
        self._task = task
        self._attr_name = task.get("name")
        self._attr_unique_id = task.get("id")
        self._attr_icon = "mdi:wrench-clock"

    @property
    def native_value(self):
        """Return the state of the sensor (OK, Warning, Critical)."""
        # A simple placeholder logic. In reality we check interval vs last_done
        return "OK"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "category": self._task.get("category"),
            "last_done": self._task.get("last_done"),
            "interval_days": self._task.get("interval_days"),
            "interval_hours": self._task.get("interval_hours"),
            "tracking_sensor": self._task.get("tracking_sensor"),
            "notes": self._task.get("notes"),
        }

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        # Read from store to get updated info
        store_data = self.hass.data[DOMAIN][self._entry_id]["data"]
        for t in store_data.get("maintenance", []):
            if t.get("id") == self._attr_unique_id:
                self._task = t
                break

class InventorySummarySensor(SensorEntity):
    """Representation of the ERP Boat Inventory Summary."""

    def __init__(self, hass: HomeAssistant, entry_id: str, inventory: list) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._entry_id = entry_id
        self._inventory = inventory
        self._attr_name = "ERP Boat Inventory Summary"
        self._attr_unique_id = f"erp_boat_inventory_{entry_id}"
        self._attr_icon = "mdi:package-variant-closed"

    @property
    def native_value(self):
        """Return the number of items below minimum stock."""
        warnings = sum(1 for item in self._inventory if item.get("quantity", 0) <= item.get("min_quantity", 0))
        return warnings

    @property
    def extra_state_attributes(self):
        """Return the entire inventory as attributes for Lovelace cards."""
        return {
            "total_items": len(self._inventory),
            "items": self._inventory
        }

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        store_data = self.hass.data[DOMAIN][self._entry_id]["data"]
        self._inventory = store_data.get("inventory", [])

class DocumentSummarySensor(SensorEntity):
    """Representation of the ERP Boat Documents Summary."""

    def __init__(self, hass: HomeAssistant, entry_id: str, documents: list) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._entry_id = entry_id
        self._documents = documents
        self._attr_name = "ERP Boat Documents"
        self._attr_unique_id = f"erp_boat_documents_{entry_id}"
        self._attr_icon = "mdi:file-document-multiple-outline"

    @property
    def native_value(self):
        """Return the number of documents expiring in < 30 days."""
        from datetime import datetime, timedelta
        warnings = 0
        today = datetime.now()
        for doc in self._documents:
            try:
                exp_date = datetime.strptime(doc.get("expiration_date", ""), "%Y-%m-%d")
                if (exp_date - today) <= timedelta(days=30):
                    warnings += 1
            except ValueError:
                pass
        return warnings

    @property
    def extra_state_attributes(self):
        """Return the documents as attributes."""
        return {
            "total_documents": len(self._documents),
            "documents": self._documents
        }

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        store_data = self.hass.data[DOMAIN][self._entry_id]["data"]
        self._documents = store_data.get("documents", [])

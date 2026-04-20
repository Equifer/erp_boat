"""The ERP Boat integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN, STORAGE_KEY, STORAGE_VERSION

_LOGGER = logging.getLogger(__name__)

# List of platforms to support (we will add sensors, buttons later)
PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ERP Boat from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Initialize storage
    _store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    data = await _store.async_load()
    if data is None:
        data = {
            "maintenance": [],
            "inventory": [],
            "tanks": [],
            "documents": []
        }
        await _store.async_save(data)

    hass.data[DOMAIN][entry.entry_id] = {
        "store": _store,
        "data": data,
    }

    async def handle_add_maintenance_task(call):
        """Handle the service call."""
        import uuid
        task = {
            "id": str(uuid.uuid4()),
            "name": call.data.get("name"),
            "category": call.data.get("category"),
            "interval_days": call.data.get("interval_days"),
            "interval_hours": call.data.get("interval_hours"),
            "tracking_sensor": call.data.get("tracking_sensor"),
            "last_done": None,
            "notes": ""
        }
        data["maintenance"].append(task)
        await _store.async_save(data)
        # Reload integration to create new sensor
        await hass.config_entries.async_reload(entry.entry_id)

    hass.services.async_register(DOMAIN, "add_maintenance_task", handle_add_maintenance_task)

    async def handle_register_maintenance_done(call):
        """Handle the service call."""
        import datetime
        task_id = call.data.get("task_id")
        notes = call.data.get("notes", "")
        
        for task in data["maintenance"]:
            if task["id"] == task_id:
                task["last_done"] = datetime.datetime.now().isoformat()
                if notes:
                    task["notes"] = f"{task.get('notes', '')}\n{datetime.date.today().isoformat()}: {notes}".strip()
                break
                
        await _store.async_save(data)
        await hass.config_entries.async_reload(entry.entry_id)

    hass.services.async_register(DOMAIN, "register_maintenance_done", handle_register_maintenance_done)

    async def handle_add_inventory_item(call):
        """Handle adding a new inventory item."""
        import uuid
        item = {
            "id": str(uuid.uuid4()),
            "name": call.data.get("name"),
            "category": call.data.get("category"),
            "reference": call.data.get("reference", ""),
            "quantity": call.data.get("quantity", 0),
            "min_quantity": call.data.get("min_quantity", 0),
            "location": call.data.get("location", "")
        }
        data["inventory"].append(item)
        await _store.async_save(data)
        await hass.config_entries.async_reload(entry.entry_id)

    hass.services.async_register(DOMAIN, "add_inventory_item", handle_add_inventory_item)

    async def handle_update_inventory_stock(call):
        """Handle updating stock of an inventory item."""
        item_id = call.data.get("item_id")
        quantity_change = call.data.get("quantity_change", 0)
        
        for item in data["inventory"]:
            if item["id"] == item_id:
                item["quantity"] = max(0, item.get("quantity", 0) + quantity_change)
                break
                
        await _store.async_save(data)
        await hass.config_entries.async_reload(entry.entry_id)

    hass.services.async_register(DOMAIN, "update_inventory_stock", handle_update_inventory_stock)

    async def handle_add_document(call):
        """Handle adding a new document."""
        import uuid
        doc = {
            "id": str(uuid.uuid4()),
            "name": call.data.get("name"),
            "expiration_date": call.data.get("expiration_date"),
            "notes": call.data.get("notes", "")
        }
        data["documents"].append(doc)
        await _store.async_save(data)
        await hass.config_entries.async_reload(entry.entry_id)

    hass.services.async_register(DOMAIN, "add_document", handle_add_document)

    # Forward the setup to the platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

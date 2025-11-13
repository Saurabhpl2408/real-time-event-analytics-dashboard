from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class PluginPriority(Enum):
    """Plugin execution priority"""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class PluginResult:
    """Result returned by plugin processing"""
    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.data = data or {}
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class EventPlugin(ABC):
    """
    Base class for all event processing plugins
    
    Each plugin can:
    - Process events
    - Enrich events with additional data
    - Generate outputs (alerts, recommendations, etc.)
    - Subscribe to specific Kafka topics
    """
    
    def __init__(self, name: str, priority: PluginPriority = PluginPriority.MEDIUM):
        self.name = name
        self.priority = priority
        self.enabled = True
    
    @abstractmethod
    async def process(self, event: Dict[str, Any]) -> PluginResult:
        """
        Process an event and return result
        
        Args:
            event: Event data dictionary
        
        Returns:
            PluginResult with processing outcome
        """
        pass
    
    @abstractmethod
    def get_kafka_topics(self) -> List[str]:
        """
        Return list of Kafka topics this plugin should consume from
        
        Returns:
            List of topic names
        """
        pass
    
    async def enrich_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich event with additional data (optional)
        
        Args:
            event: Original event data
        
        Returns:
            Enriched event data
        """
        return event
    
    def should_process(self, event: Dict[str, Any]) -> bool:
        """
        Determine if this plugin should process the event
        
        Args:
            event: Event data
        
        Returns:
            True if plugin should process this event
        """
        return self.enabled
    
    async def on_startup(self):
        """Called when plugin is initialized"""
        pass
    
    async def on_shutdown(self):
        """Called when plugin is shutting down"""
        pass


class PluginManager:
    """
    Manages all event processing plugins
    Coordinates plugin execution and maintains plugin registry
    """
    
    def __init__(self):
        self.plugins: List[EventPlugin] = []
        self._initialized = False
    
    def register_plugin(self, plugin: EventPlugin):
        """Register a new plugin"""
        if plugin not in self.plugins:
            self.plugins.append(plugin)
            # Sort by priority
            self.plugins.sort(key=lambda p: p.priority.value)
            print(f"[PluginManager] Registered plugin: {plugin.name}")
    
    def unregister_plugin(self, plugin_name: str):
        """Unregister a plugin by name"""
        self.plugins = [p for p in self.plugins if p.name != plugin_name]
    
    def get_plugin(self, plugin_name: str) -> Optional[EventPlugin]:
        """Get plugin by name"""
        for plugin in self.plugins:
            if plugin.name == plugin_name:
                return plugin
        return None
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all registered plugins"""
        return [
            {
                "name": p.name,
                "priority": p.priority.name,
                "enabled": p.enabled,
                "topics": p.get_kafka_topics()
            }
            for p in self.plugins
        ]
    
    async def process_event(self, event: Dict[str, Any]) -> Dict[str, PluginResult]:
        """
        Process event through all registered plugins
        
        Args:
            event: Event data
        
        Returns:
            Dictionary mapping plugin names to their results
        """
        results = {}
        
        for plugin in self.plugins:
            if not plugin.should_process(event):
                continue
            
            try:
                # Enrich event if needed
                enriched_event = await plugin.enrich_event(event)
                
                # Process event
                result = await plugin.process(enriched_event)
                results[plugin.name] = result
                
            except Exception as e:
                results[plugin.name] = PluginResult(
                    success=False,
                    error=f"Plugin error: {str(e)}"
                )
        
        return results
    
    def get_all_kafka_topics(self) -> List[str]:
        """Get all Kafka topics that plugins are subscribed to"""
        topics = set()
        for plugin in self.plugins:
            topics.update(plugin.get_kafka_topics())
        return list(topics)
    
    async def startup(self):
        """Initialize all plugins"""
        if self._initialized:
            return
        
        print("[PluginManager] Initializing plugins...")
        for plugin in self.plugins:
            try:
                await plugin.on_startup()
                print(f"[PluginManager] Initialized: {plugin.name}")
            except Exception as e:
                print(f"[PluginManager] Failed to initialize {plugin.name}: {e}")
        
        self._initialized = True
    
    async def shutdown(self):
        """Shutdown all plugins"""
        print("[PluginManager] Shutting down plugins...")
        for plugin in self.plugins:
            try:
                await plugin.on_shutdown()
                print(f"[PluginManager] Shutdown: {plugin.name}")
            except Exception as e:
                print(f"[PluginManager] Error shutting down {plugin.name}: {e}")
        
        self._initialized = False


# Global plugin manager instance
plugin_manager = PluginManager()
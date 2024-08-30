import psutil
import platform
from . import Capability, export
from typing import Dict, Any

class SystemInfoCapability(Capability):
    @staticmethod
    def name() -> str:
        return "systemInfo"

    @export
    def get_cpu_usage(self, v) -> list[float]:
        """ Returns the CPU usage percentage. """
        return psutil.cpu_percent(interval=None, percpu=True)

    @export
    def get_memory_info(self, v) -> Dict[str, Any]:
        """ Returns memory usage statistics. """
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent
        }

    @export
    def get_disk_usage(self, v) -> Dict[str, Any]:
        """ Returns disk usage statistics. """
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }

    @export
    def get_system_info(self, v) -> Dict[str, str]:
        """ Returns basic system information. """
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor()
        }

    @export
    def get_gpu_usage(self, v) -> Dict[str, Any]:
        """ Returns GPU usage statistics. """
        raise NotImplemented("Sorry")

import hashlib
import platform
import subprocess
import os
from utils.logger import get_logger

logger = get_logger(__name__)

def get_hwid():
    """Get unique machine identifier for Windows, Mac, and Linux."""
    try:
        system = platform.system()
        hwid_raw = ""
        
        if system == "Windows":
            try:
                import wmi
                c = wmi.WMI()
                cpu_id = c.Win32_Processor()[0].ProcessorId.strip()
                board_id = c.Win32_BaseBoard()[0].SerialNumber.strip()
                hwid_raw = f"{cpu_id}-{board_id}"
            except Exception as e:
                logger.warning(f"WMI failed, falling back to powershell: {e}")
                cpu_id = subprocess.check_output("wmic cpu get processorid", shell=True).decode().split('\n')[1].strip()
                board_id = subprocess.check_output("wmic baseboard get serialnumber", shell=True).decode().split('\n')[1].strip()
                hwid_raw = f"{cpu_id}-{board_id}"
                
        elif system == "Darwin":  # macOS
            # Get IOPlatformUUID
            cmd = "ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID"
            output = subprocess.check_output(cmd, shell=True).decode()
            hwid_raw = output.split('=')[-1].strip().replace('"', '')
            
        elif system == "Linux":
            # Get machine-id
            if os.path.exists("/etc/machine-id"):
                with open("/etc/machine-id", "r") as f:
                    hwid_raw = f.read().strip()
            elif os.path.exists("/var/lib/dbus/machine-id"):
                with open("/var/lib/dbus/machine-id", "r") as f:
                    hwid_raw = f.read().strip()
            else:
                # Fallback to cpuinfo
                cmd = "cat /proc/cpuinfo | grep Serial | cut -d ':' -f 2"
                hwid_raw = subprocess.check_output(cmd, shell=True).decode().strip()
        
        if not hwid_raw:
            # Final fallback
            import uuid
            hwid_raw = str(uuid.getnode())
            
        return hashlib.sha256(hwid_raw.encode()).hexdigest()
    except Exception as e:
        logger.error(f"Failed to get HWID: {e}")
        # Return a fallback based on node name
        return hashlib.sha256(platform.node().encode()).hexdigest()

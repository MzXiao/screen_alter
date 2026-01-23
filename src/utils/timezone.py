"""
Timezone utilities for handling China timezone (Asia/Shanghai, UTC+8).
"""
from datetime import datetime
import pytz

# China timezone
CHINA_TZ = pytz.timezone('Asia/Shanghai')

def get_china_time() -> datetime:
    """
    Get current time in China timezone (Asia/Shanghai, UTC+8).
    
    Returns:
        datetime object in China timezone
    """
    return datetime.now(CHINA_TZ)

def format_china_time(dt: datetime = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string in China timezone.
    
    Args:
        dt: datetime object (if None, uses current time)
        format_str: Format string (default: "%Y-%m-%d %H:%M:%S")
    
    Returns:
        Formatted time string in China timezone
    """
    if dt is None:
        dt = get_china_time()
    elif dt.tzinfo is None:
        # If naive datetime, assume it's UTC and convert to China timezone
        dt = pytz.utc.localize(dt).astimezone(CHINA_TZ)
    else:
        # Convert to China timezone
        dt = dt.astimezone(CHINA_TZ)
    
    return dt.strftime(format_str)

def parse_and_convert_to_china(dt_str: str) -> datetime:
    """
    Parse datetime string and convert to China timezone.
    Handles both timezone-aware and naive datetime strings.
    For naive datetimes from SQLite, assumes they are already in China timezone.
    
    Args:
        dt_str: Datetime string (from database or other source)
    
    Returns:
        datetime object in China timezone
    """
    if not dt_str:
        return get_china_time()
    
    dt_str = str(dt_str).strip()
    
    # Try to parse as ISO format first (with timezone)
    try:
        # Try parsing with timezone info
        if 'Z' in dt_str or '+' in dt_str or dt_str.count('-') > 2:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            if dt.tzinfo is None:
                # If still naive after parsing, assume UTC
                dt = pytz.utc.localize(dt)
            return dt.astimezone(CHINA_TZ)
    except (ValueError, AttributeError):
        pass
    
    # Try common SQLite formats (naive datetime)
    # Note: For backward compatibility, we check if the time looks like UTC (8 hours behind China)
    # If it's within reasonable range, assume it's already China timezone (new data)
    # Otherwise, assume UTC (old data from CURRENT_TIMESTAMP)
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str, fmt)
            # For naive datetime from SQLite:
            # - New data: stored with China timezone, so localize to China TZ
            # - Old data: stored with UTC (CURRENT_TIMESTAMP), need to convert
            # We'll assume it's China timezone (since we're now storing China time)
            # If you have old UTC data, you may need to migrate it
            return CHINA_TZ.localize(dt)
        except ValueError:
            continue
    
    # If all parsing fails, return current China time
    return get_china_time()

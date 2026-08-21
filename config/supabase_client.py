"""
Supabase client initialization and utilities.
Uses the official supabase-py client for database access.
ALL operations use this single client instance - NO direct REST API calls.
"""

import logging
import json
import traceback
import uuid
from typing import Optional, Dict, Any
from supabase import create_client, Client
from postgrest.exceptions import APIError

logger = logging.getLogger(__name__)


def identify_key_type(key: str) -> str:
    """Identify if key is ANON or SERVICE_ROLE"""
    if key.startswith("sb_publishable_"):
        return "ANON (public, limited access)"
    elif key.startswith("sb_secret_"):
        return "SERVICE_ROLE (admin, full access)"
    else:
        return "UNKNOWN"


def extract_error_details(error: Exception) -> Dict[str, Any]:
    """
    Extract complete error details from Supabase/Postgrest exceptions.
    Returns structured error information without suppressing details.
    """
    details = {
        "type": type(error).__name__,
        "message": str(error),
        "status_code": None,
        "error_code": None,
        "error_details": None,
        "hint": None,
        "is_rls_blocked": False,
        "traceback": traceback.format_exc()
    }
    
    # Handle APIError (from postgrest)
    if isinstance(error, APIError):
        details["status_code"] = getattr(error, 'code', None)
        details["error_code"] = getattr(error, 'error', None)
        details["error_details"] = getattr(error, 'message', None)
        details["hint"] = getattr(error, 'hint', None)
        
        # Check for RLS
        error_msg = str(error).lower()
        if "row-level security" in error_msg or "rls" in error_msg or "42501" in str(error):
            details["is_rls_blocked"] = True
    
    # Handle response-based errors
    if hasattr(error, 'resp'):
        try:
            resp = error.resp
            details["status_code"] = getattr(resp, 'status', None)
            
            if hasattr(resp, 'content'):
                try:
                    if isinstance(resp.content, str):
                        body = json.loads(resp.content)
                    else:
                        body = resp.content
                    
                    details["error_details"] = body.get('message', body)
                    details["hint"] = body.get('hint')
                    
                    # Check for RLS error code
                    if body.get('code') == '42501':
                        details["is_rls_blocked"] = True
                except:
                    pass
        except:
            pass
    
    return details


def get_supabase_client() -> Client:
    """
    Initialize Supabase client using Django settings.
    Settings are already loaded from .env via django.conf.settings.
    """
    from django.conf import settings
    
    url = settings.SUPABASE_URL
    key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "") or settings.SUPABASE_ANON_KEY
    key_type = identify_key_type(key)
    
    logger.info(f"🔌 Initializing Supabase client")
    logger.info(f"   URL: {url}")
    logger.info(f"   Key Type: {key_type}")
    logger.info(f"   Key Length: {len(key) if key else 0} chars")
    
    if not url or not key:
        error_msg = (
            "SUPABASE_URL and SUPABASE_ANON_KEY must be set in Django settings. "
            "Check config/settings/local.py and .env file."
        )
        logger.error(f"❌ Missing Supabase config: {error_msg}")
        raise ValueError(error_msg)
    
    try:
        client = create_client(url, key)
        logger.info(f"✅ Supabase client created successfully")
        return client
    except Exception as e:
        error_details = extract_error_details(e)
        logger.error(f"❌ Failed to create Supabase client")
        logger.error(f"   Type: {error_details['type']}")
        logger.error(f"   Message: {error_details['message']}")
        logger.error(f"   Status: {error_details['status_code']}")
        logger.error(f"   Traceback:\n{error_details['traceback']}")
        raise


class SupabaseService:
    """
    Service layer for Supabase database operations.
    Singleton pattern ensures only ONE client instance is used for all operations.
    Uses specific exception handling for Supabase API errors.
    """
    
    def __init__(self):
        logger.info("🔧 Initializing SupabaseService")
        self.client = get_supabase_client()
        logger.info("✅ SupabaseService ready")
    
    def _handle_error(self, operation: str, table: str, error: Exception):
        """
        Handle Supabase errors with detailed logging.
        Does NOT suppress error details.
        """
        error_details = extract_error_details(error)
        
        logger.error(f"❌ Error during {operation} on table '{table}'")
        logger.error(f"   Type: {error_details['type']}")
        logger.error(f"   Message: {error_details['message']}")
        
        if error_details['status_code']:
            logger.error(f"   Status Code: {error_details['status_code']}")
        
        if error_details['error_code']:
            logger.error(f"   Error Code: {error_details['error_code']}")
        
        if error_details['error_details']:
            logger.error(f"   Details: {error_details['error_details']}")
        
        if error_details['hint']:
            logger.error(f"   Hint: {error_details['hint']}")
        
        if error_details['is_rls_blocked']:
            logger.error(f"\n   🔒 DIAGNOSIS: Row Level Security (RLS) Policy")
            logger.error(f"   → Table '{table}' has RLS policies blocking operations")
            logger.error(f"   → ANON key cannot bypass RLS")
            logger.error(f"   → FIX: Disable RLS in Supabase SQL Editor:")
            logger.error(f"      ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
        
        logger.debug(f"   Full Traceback:\n{error_details['traceback']}")
        
        # Re-raise the original exception
        raise
    
    # ============= Users =============
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch user profile from users table."""
        try:
            logger.debug(f"📖 Fetching user: {user_id}")
            response = self.client.table("users").select("*").eq("id", user_id).maybe_single().execute()
            # Handle None response
            if response is None:
                logger.warning(f"   ⚠️  Supabase returned None response for user {user_id}")
                return None
            result = response.data if response.data else None
            logger.debug(f"   ✅ User found: {bool(result)}")
            return result
        except APIError as e:
            self._handle_error("SELECT", "users", e)
        except Exception as e:
            self._handle_error("SELECT", "users", e)
    
    def create_user(self, user_id: str, username: str) -> Optional[Dict[str, Any]]:
        """Create new user profile in users table."""
        try:
            logger.debug(f"✍️ Creating user: {user_id} with username: {username}")
            response = self.client.table("users").insert({
                "id": user_id,
                "username": username
            }).execute()
            
            if response is None:
                logger.warning(f"   ⚠️  Supabase returned None response for insert")
                return None
            
            result = response.data if response.data else None
            logger.debug(f"   ✅ User created: {bool(result)}")
            return result
        except APIError as e:
            logger.error(f"   ❌ API Error: {e}")
            self._handle_error("INSERT", "users", e)
            return None
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            self._handle_error("INSERT", "users", e)
            return None
    
    def update_user(self, user_id: str, username: str) -> Optional[Dict[str, Any]]:
        """Update user profile in users table."""
        try:
            logger.debug(f"✏️ Updating user: {user_id} with username: {username}")
            response = self.client.table("users").update({
                "username": username
            }).eq("id", user_id).execute()
            
            if response is None:
                logger.warning(f"   ⚠️  Supabase returned None response for update")
                return None
            
            result = response.data if response.data else None
            logger.debug(f"   ✅ User updated: {bool(result)}")
            return result
        except APIError as e:
            logger.error(f"   ❌ API Error: {e}")
            self._handle_error("UPDATE", "users", e)
            return None
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            self._handle_error("UPDATE", "users", e)
            return None
    
    # ============= Devices =============
    def get_user_devices(self, user_id: str) -> list:
        """Fetch all devices for a user."""
        try:
            logger.debug(f"📖 Fetching devices for user: {user_id}")
            response = self.client.table("devices").select("*").eq("owner_id", user_id).execute()
            if response is None:
                logger.warning(f"   ⚠️  Supabase returned None response for user {user_id}")
                return []
            result = response.data if response.data else []
            logger.debug(f"   ✅ Found {len(result)} devices")
            return result
        except APIError as e:
            self._handle_error("SELECT", "devices", e)
        except Exception as e:
            self._handle_error("SELECT", "devices", e)
    
    def get_device(self, device_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch single device (ensure it belongs to authenticated user)."""
        try:
            logger.debug(f"📖 Fetching device {device_id} for user {user_id}")
            response = (
                self.client.table("devices")
                .select("*")
                .eq("device_id", device_id)
                .eq("owner_id", user_id)
                .maybe_single()
                .execute()
            )
            if response is None:
                logger.warning(f"   ⚠️  Supabase returned None response for device {device_id}")
                return None
            result = response.data if response.data else None
            logger.debug(f"   ✅ Device found: {bool(result)}")
            return result
        except APIError as e:
            self._handle_error("SELECT", "devices", e)
        except Exception as e:
            self._handle_error("SELECT", "devices", e)
    
    def update_device_location(self, device_id: str, user_id: str, location: str) -> bool:
        """Update device location (ensure device belongs to authenticated user)."""
        try:
            logger.debug(f"📝 Updating location for device {device_id}: {location}")
            
            # First verify device belongs to user
            device = self.get_device(device_id, user_id)
            if not device:
                logger.warning(f"   ⚠️ Device {device_id} not found or doesn't belong to user {user_id}")
                return False
            
            # Update location
            response = (
                self.client.table("devices")
                .update({"location": location})
                .eq("device_id", device_id)
                .eq("owner_id", user_id)
                .execute()
            )
            
            if response is None:
                logger.warning(f"   ⚠️  Supabase returned None response when updating location")
                return False
            
            logger.debug(f"   ✅ Location updated successfully")
            return True
        except APIError as e:
            self._handle_error("UPDATE", "devices", e)
            return False
        except Exception as e:
            self._handle_error("UPDATE", "devices", e)
            return False

    # ============= Transport profiles =============
    _TRANSPORT_PROFILE_PREFIX = "transport-profile:"

    @staticmethod
    def _format_transport_profile(profile: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Expose the profiles-table name column through the UI's profile_name key."""
        if not profile:
            return None
        name = profile.get("name", "")
        if not isinstance(name, str):
            return None
        if not name.startswith(SupabaseService._TRANSPORT_PROFILE_PREFIX):
            legacy_columns = {
                "temperatura": ("temperature_min", "temperature_max"),
                "umiditate": ("humidity_min", "humidity_max"),
                "co2": ("co2_min", "co2_max"),
                "pm25": ("pm25_min", "pm25_max"),
                "pm10": ("pm10_min", "pm10_max"),
            }
            thresholds = {
                parameter: {"minimum": profile[minimum], "maximum": profile[maximum]}
                for parameter, (minimum, maximum) in legacy_columns.items()
                if profile.get(minimum) is not None and profile.get(maximum) is not None
            }
            if not thresholds:
                return None
            return {
                **profile,
                "profile_name": name or "Profil legacy",
                "thresholds": thresholds,
                "is_active": True,
            }
        try:
            profile_data = json.loads(name.removeprefix(SupabaseService._TRANSPORT_PROFILE_PREFIX))
        except json.JSONDecodeError:
            return None
        if "thresholds" not in profile_data and profile_data.get("parameter"):
            profile_data["thresholds"] = {
                profile_data["parameter"]: {
                    "minimum": profile_data.get("minimum_value"),
                    "maximum": profile_data.get("maximum_value"),
                }
            }
        return {**profile, **profile_data, "profile_name": profile_data.get("profile_name", "")}

    @classmethod
    def _serialize_transport_profile(cls, profile_data: Dict[str, Any]) -> str:
        """Store profile settings in profiles.name until dedicated columns are available."""
        return cls._TRANSPORT_PROFILE_PREFIX + json.dumps(profile_data, separators=(",", ":"))

    @staticmethod
    def _threshold_column_values(thresholds: Dict[str, Dict[str, float]]) -> Dict[str, Optional[float]]:
        """Map profile parameters onto the dedicated threshold columns already in profiles."""
        column_prefixes = {
            "temperatura": "temperature",
            "umiditate": "humidity",
            "co2": "co2",
            "pm25": "pm25",
            "pm10": "pm10",
        }
        values = {}
        for parameter, prefix in column_prefixes.items():
            threshold = thresholds.get(parameter)
            values[f"{prefix}_min"] = threshold.get("minimum") if threshold else None
            values[f"{prefix}_max"] = threshold.get("maximum") if threshold else None
        return values

    @staticmethod
    def _has_missing_profiles_column(error: Exception) -> bool:
        """Detect an unapplied transport-profile migration without hiding other API errors."""
        error_message = str(error)
        return isinstance(error, APIError) and (
            ("column profiles." in error_message and "does not exist" in error_message)
            or "'code': 'PGRST204'" in error_message
        )

    @staticmethod
    def _is_empty_profiles_response(error: Exception) -> bool:
        """Postgrest-py represents a 204 result from maybe_single as APIError."""
        return isinstance(error, APIError) and "'code': '204'" in str(error)

    @staticmethod
    def _is_profiles_rls_denial(error: Exception) -> bool:
        """Recognize RLS denials so the UI can report a configuration issue safely."""
        return isinstance(error, APIError) and "'code': '42501'" in str(error)

    def get_transport_profiles(self, device_id: str, user_id: str) -> list:
        """List custom parameter profiles configured for an owned device."""
        device = self.get_device(device_id, user_id)
        if not device:
            return []

        try:
            response = self.client.table("profiles").select("*").eq("user_id", user_id).execute()
            profiles = [self._format_transport_profile(profile) for profile in (response.data or [])]
            return [profile for profile in profiles if profile and profile.get("device_id") == device_id]
        except APIError as e:
            if self._has_missing_profiles_column(e):
                logger.warning("Transport profile migration is not applied yet: %s", e)
                return []
            self._handle_error("SELECT", "profiles", e)
        except Exception as e:
            self._handle_error("SELECT", "profiles", e)

    def get_transport_profile(self, device_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch the active custom parameter profile configured for an owned device."""
        device = self.get_device(device_id, user_id)
        if not device:
            return None

        try:
            profiles = self.get_transport_profiles(device_id, user_id)
            return next((profile for profile in profiles if profile.get("is_active")), None)
        except APIError as e:
            if self._has_missing_profiles_column(e):
                logger.warning("Transport profile migration is not applied yet: %s", e)
                return None
            if self._is_empty_profiles_response(e):
                return None
            self._handle_error("SELECT", "profiles", e)
        except Exception as e:
            self._handle_error("SELECT", "profiles", e)

    def save_transport_profile(
        self,
        device_id: str,
        user_id: str,
        profile_name: str,
        thresholds: Dict[str, Dict[str, float]],
        notes: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Create a custom parameter profile in profiles for an owned device."""
        device = self.get_device(device_id, user_id)
        if not device:
            return None

        try:
            profile_data = {
                "device_id": device_id,
                "profile_name": profile_name,
                "thresholds": thresholds,
                "is_active": False,
                "notes": notes,
            }
            profile_row = {
                "user_id": user_id,
                "device_id": device_id,
                "name": self._serialize_transport_profile(profile_data),
            }
            profile_row.update(self._threshold_column_values(thresholds))
            response = self.client.table("profiles").insert(profile_row).execute()
            return self._format_transport_profile(response.data[0] if response and response.data else None)
        except APIError as e:
            if self._has_missing_profiles_column(e):
                logger.warning("Transport profile migration is not applied yet: %s", e)
                return None
            if self._is_profiles_rls_denial(e):
                logger.warning("Profiles insert blocked by RLS: %s", e)
                return None
            self._handle_error("UPSERT", "profiles", e)
        except Exception as e:
            self._handle_error("UPSERT", "profiles", e)

    def update_transport_profile(
        self,
        device_id: str,
        profile_id: str,
        user_id: str,
        profile_name: str,
        thresholds: Dict[str, Dict[str, float]],
        notes: str = "",
    ) -> bool:
        """Update a named profile and its independent parameter thresholds."""
        profiles = self.get_transport_profiles(device_id, user_id)
        profile = next((item for item in profiles if str(item.get("id")) == profile_id), None)
        if not profile:
            return False
        profile_data = {
            "device_id": device_id,
            "profile_name": profile_name,
            "thresholds": thresholds,
            "is_active": profile.get("is_active", False),
            "notes": notes,
        }
        try:
            profile_row = {
                "name": self._serialize_transport_profile(profile_data),
            }
            profile_row.update(self._threshold_column_values(thresholds))
            response = self.client.table("profiles").update(profile_row).eq("id", profile_id).eq("user_id", user_id).execute()
            return bool(response and response.data)
        except APIError as e:
            if self._is_profiles_rls_denial(e):
                logger.warning("Profiles update blocked by RLS: %s", e)
                return False
            self._handle_error("UPDATE", "profiles", e)

    def delete_transport_profile(self, device_id: str, profile_id: str, user_id: str) -> bool:
        """Delete one owned custom profile from profiles."""
        profiles = self.get_transport_profiles(device_id, user_id)
        if not any(str(profile.get("id")) == profile_id for profile in profiles):
            return False
        try:
            response = self.client.table("profiles").delete().eq("id", profile_id).eq("user_id", user_id).execute()
            return bool(response and response.data)
        except APIError as e:
            if self._is_profiles_rls_denial(e):
                logger.warning("Profiles delete blocked by RLS: %s", e)
                return False
            self._handle_error("DELETE", "profiles", e)

    def activate_transport_profile(self, device_id: str, profile_id: str, user_id: str) -> bool:
        """Make one custom profile active for an owned device."""
        device = self.get_device(device_id, user_id)
        if not device:
            return False

        try:
            profiles = self.get_transport_profiles(device_id, user_id)
            selected_profile = next((profile for profile in profiles if str(profile.get("id")) == profile_id), None)
            if not selected_profile:
                return False
            for profile in profiles:
                profile_data = {
                    "device_id": profile["device_id"],
                    "profile_name": profile["profile_name"],
                    "thresholds": profile.get("thresholds", {}),
                    "is_active": profile["id"] == selected_profile["id"],
                    "notes": profile.get("notes", ""),
                }
                self.client.table("profiles").update({"name": self._serialize_transport_profile(profile_data)}).eq("id", profile["id"]).eq("user_id", user_id).execute()
            return True
        except APIError as e:
            if self._has_missing_profiles_column(e):
                logger.warning("Transport profile migration is not applied yet: %s", e)
                return False
            self._handle_error("UPDATE", "profiles", e)
        except Exception as e:
            self._handle_error("UPDATE", "profiles", e)

    def activate_standard_transport_profile(self, device_id: str, user_id: str) -> bool:
        """Make the built-in Standard profile active by disabling custom profiles."""
        profiles = self.get_transport_profiles(device_id, user_id)
        try:
            for profile in profiles:
                profile_data = {
                    "device_id": profile["device_id"],
                    "profile_name": profile["profile_name"],
                    "thresholds": profile.get("thresholds", {}),
                    "is_active": False,
                    "notes": profile.get("notes", ""),
                }
                self.client.table("profiles").update({
                    "name": self._serialize_transport_profile(profile_data),
                }).eq("id", profile["id"]).eq("user_id", user_id).execute()
            return True
        except APIError as e:
            if self._is_profiles_rls_denial(e):
                logger.warning("Standard profile activation blocked by RLS: %s", e)
                return False
            self._handle_error("UPDATE", "profiles", e)
    
    # ============= Measurements =============
    def get_device_measurements(self, device_id: str, user_id: str, limit: int = 100) -> list:
        """
        Fetch measurements for a device.
        Only returns data if device belongs to authenticated user.
        """
        try:
            logger.debug(f"📖 Fetching measurements for device {device_id} (limit={limit})")
            
            # First verify device belongs to user
            device = self.get_device(device_id, user_id)
            if not device:
                logger.warning(f"   ⚠️  Device {device_id} does not belong to user {user_id}")
                return []
            
            response = (
                self.client.table("measurements")
                .select("*")
                .eq("device_id", device_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            if response is None:
                logger.warning(f"   ⚠️  Supabase returned None response for measurements")
                return []
            result = response.data if response.data else []
            logger.debug(f"   ✅ Found {len(result)} measurements")
            return result
        except APIError as e:
            self._handle_error("SELECT", "measurements", e)
        except Exception as e:
            self._handle_error("SELECT", "measurements", e)
    
    def get_latest_measurement(self, device_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch the latest measurement for a device."""
        try:
            logger.debug(f"📖 Fetching latest measurement for device {device_id}")
            measurements = self.get_device_measurements(device_id, user_id, limit=1)
            result = measurements[0] if measurements else None
            if result:
                logger.debug(f"   ✅ Latest measurement keys: {list(result.keys())}")
                logger.debug(f"   📦 Latest measurement data: {result}")
            else:
                logger.debug(f"   ✅ Latest measurement found: {bool(result)}")
            return result
        except APIError as e:
            self._handle_error("SELECT", "measurements", e)
        except Exception as e:
            self._handle_error("SELECT", "measurements", e)
    
    def get_measurements_for_dashboard(self, device_id: str, user_id: str, limit: int = 1000) -> list:
        """
        Fetch measurements for dashboard graphs.
        Includes all sensor fields needed for charts.
        Returns in chronological order (oldest to newest).
        """
        try:
            logger.debug(f"📖 Fetching dashboard measurements for device {device_id}")
            measurements = self.get_device_measurements(device_id, user_id, limit=limit)
            # Reverse to get chronological order for charts
            result = list(reversed(measurements))
            logger.debug(f"   ✅ Dashboard measurements: {len(result)} items")
            return result
        except APIError as e:
            self._handle_error("SELECT", "measurements", e)
        except Exception as e:
            self._handle_error("SELECT", "measurements", e)
    
    # ============= QR Login =============
    def create_login_request(self, expires_at: str) -> Optional[Dict[str, Any]]:
        """
        Create a new QR login request (status=pending, user_id=NULL).
        Generates a UUID token for the QR code.
        
        Table schema: web_login_requests
        - id: UUID (primary key, auto-generated)
        - token: UUID (NOT NULL, used in QR code)
        - status: VARCHAR (pending/approved/expired)
        - user_id: UUID (NULL initially)
        - expires_at: TIMESTAMPTZ
        - approved_at: TIMESTAMPTZ (NULL initially)
        - created_at: TIMESTAMPTZ (auto-set)
        """
        try:
            # Generate UUID for token (this is what goes in QR code)
            token = str(uuid.uuid4())
            
            insert_data = {
                "token": token,
                "status": "pending",
                "user_id": None,
                "expires_at": expires_at
            }
            
            logger.info(f"📝 Creating QR login request")
            logger.debug(f"   Token: {token}")
            logger.debug(f"   Data: {json.dumps(insert_data, default=str)}")
            
            response = (
                self.client.table("web_login_requests")
                .insert(insert_data)
                .execute()
            )
            
            if response is None:
                logger.error(f"❌ Supabase returned None response for insert")
                return None
            result = response.data[0] if response.data else None
            
            if result:
                logger.info(f"✅ QR login request created: {result.get('id')}")
                logger.debug(f"   Token: {result.get('token')}")
                logger.debug(f"   Status: {result.get('status')}")
                logger.debug(f"   Expires: {result.get('expires_at')}")
            else:
                logger.error(f"❌ INSERT succeeded but returned no data")
                logger.error(f"   Response: {response}")
            
            return result
            
        except APIError as e:
            self._handle_error("INSERT", "web_login_requests", e)
        except Exception as e:
            self._handle_error("INSERT", "web_login_requests", e)
    
    def get_login_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a login request by ID."""
        try:
            logger.debug(f"📖 Fetching login request: {request_id}")
            response = (
                self.client.table("web_login_requests")
                .select("*")
                .eq("id", request_id)
                .maybe_single()
                .execute()
            )
            if response is None:
                logger.warning(f"   ⚠️  Supabase returned None response for login request")
                return None
            result = response.data if response.data else None
            
            if result:
                logger.debug(f"   ✅ Found - Status: {result.get('status')}")
            else:
                logger.debug(f"   ⚠️  Not found")
            
            return result
            
        except APIError as e:
            self._handle_error("SELECT", "web_login_requests", e)
        except Exception as e:
            self._handle_error("SELECT", "web_login_requests", e)
    
    def update_login_request(self, request_id: str, data: dict) -> Optional[Dict[str, Any]]:
        """
        Update a login request.
        Typically used to set: user_id, status='approved', approved_at.
        """
        try:
            logger.info(f"🔄 Updating login request {request_id}")
            logger.debug(f"   Fields: {list(data.keys())}")
            logger.debug(f"   Data: {json.dumps(data, default=str)}")
            
            response = (
                self.client.table("web_login_requests")
                .update(data)
                .eq("id", request_id)
                .execute()
            )
            
            if response is None:
                logger.error(f"❌ Supabase returned None response for update")
                return None
            result = response.data[0] if response.data else None
            
            if result:
                logger.info(f"✅ Login request updated")
                logger.debug(f"   New Status: {result.get('status')}")
                logger.debug(f"   User ID: {result.get('user_id')}")
            else:
                logger.error(f"❌ UPDATE succeeded but returned no data")
                logger.error(f"   Response: {response}")
            
            return result
            
        except APIError as e:
            self._handle_error("UPDATE", "web_login_requests", e)
        except Exception as e:
            self._handle_error("UPDATE", "web_login_requests", e)

# Singleton instance - ONE client for entire application
_service: Optional['SupabaseService'] = None


def get_service() -> SupabaseService:
    """
    Get or create the Supabase service singleton.
    Ensures only ONE client instance is used application-wide.
    """
    global _service
    if _service is None:
        logger.info("📦 Creating SupabaseService singleton")
        _service = SupabaseService()
    return _service

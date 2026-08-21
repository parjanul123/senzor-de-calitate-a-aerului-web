-- Store client-managed transport settings in the existing public.profiles table.
-- The profile name is fully chosen by the transport company and is stored in name.

ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS device_id text,
    ADD COLUMN IF NOT EXISTS cargo_name text,
    ADD COLUMN IF NOT EXISTS minimum_temperature numeric(6, 2),
    ADD COLUMN IF NOT EXISTS maximum_temperature numeric(6, 2),
    ADD COLUMN IF NOT EXISTS notes text;

ALTER TABLE public.profiles
    DROP CONSTRAINT IF EXISTS profiles_transport_temperature_range_check,
    ADD CONSTRAINT profiles_transport_temperature_range_check
        CHECK (
            minimum_temperature IS NULL
            OR maximum_temperature IS NULL
            OR minimum_temperature < maximum_temperature
        );

ALTER TABLE public.profiles
    DROP CONSTRAINT IF EXISTS profiles_device_id_key,
    ADD CONSTRAINT profiles_device_id_key UNIQUE (device_id);

CREATE INDEX IF NOT EXISTS profiles_user_id_idx
    ON public.profiles (user_id);

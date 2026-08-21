-- Allow multiple named, parameter-specific profiles for each device.
-- Existing temperature profiles are retained as custom temperature profiles.

ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS device_id text,
    ADD COLUMN IF NOT EXISTS cargo_name text,
    ADD COLUMN IF NOT EXISTS minimum_temperature numeric(6, 2),
    ADD COLUMN IF NOT EXISTS maximum_temperature numeric(6, 2),
    ADD COLUMN IF NOT EXISTS notes text,
    ADD COLUMN IF NOT EXISTS parameter text,
    ADD COLUMN IF NOT EXISTS minimum_value numeric(12, 3),
    ADD COLUMN IF NOT EXISTS maximum_value numeric(12, 3),
    ADD COLUMN IF NOT EXISTS is_active boolean NOT NULL DEFAULT false;

UPDATE public.profiles
SET
    parameter = COALESCE(parameter, 'temperatura'),
    minimum_value = COALESCE(minimum_value, minimum_temperature),
    maximum_value = COALESCE(maximum_value, maximum_temperature)
WHERE device_id IS NOT NULL;

ALTER TABLE public.profiles
    DROP CONSTRAINT IF EXISTS profiles_device_id_key,
    DROP CONSTRAINT IF EXISTS profiles_parameter_range_check,
    ADD CONSTRAINT profiles_parameter_range_check
        CHECK (
            minimum_value IS NULL
            OR maximum_value IS NULL
            OR minimum_value < maximum_value
        );

CREATE UNIQUE INDEX IF NOT EXISTS profiles_one_active_per_device_idx
    ON public.profiles (device_id)
    WHERE is_active AND device_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS profiles_device_id_idx
    ON public.profiles (device_id);

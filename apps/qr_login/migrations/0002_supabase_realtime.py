from django.db import migrations


def create_supabase_objects(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    schema_editor.execute(
        """
        CREATE OR REPLACE FUNCTION public.notify_web_login_request_approved()
        RETURNS trigger
        LANGUAGE plpgsql
        SECURITY DEFINER
        SET search_path = public, realtime
        AS $$
        BEGIN
            IF NEW.status = 'approved' AND OLD.status IS DISTINCT FROM 'approved' THEN
                PERFORM realtime.send(
                    jsonb_build_object('status', 'approved'),
                    'approved',
                    'qr-login:' || NEW.token::text,
                    false
                );
            END IF;
            RETURN NEW;
        END;
        $$;

        DROP TRIGGER IF EXISTS web_login_request_approved_broadcast ON public.web_login_requests;
        CREATE TRIGGER web_login_request_approved_broadcast
        AFTER UPDATE ON public.web_login_requests
        FOR EACH ROW EXECUTE FUNCTION public.notify_web_login_request_approved();

        ALTER TABLE public.web_login_requests ENABLE ROW LEVEL SECURITY;
        REVOKE ALL ON TABLE public.web_login_requests FROM anon, authenticated;

        CREATE OR REPLACE FUNCTION public.approve_web_login_request(request_token uuid)
        RETURNS void
        LANGUAGE plpgsql
        SECURITY DEFINER
        SET search_path = public
        AS $$
        DECLARE
            updated_count integer;
        BEGIN
            UPDATE public.web_login_requests
            SET status = 'approved', user_id = auth.uid(), approved_at = timezone('utc', now())
            WHERE token = request_token
              AND status = 'pending'
              AND expires_at > timezone('utc', now())
              AND consumed_at IS NULL;

            GET DIAGNOSTICS updated_count = ROW_COUNT;
            IF updated_count != 1 THEN
                RAISE EXCEPTION 'QR login request is invalid or expired' USING ERRCODE = 'P0001';
            END IF;
        END;
        $$;

        REVOKE ALL ON FUNCTION public.approve_web_login_request(uuid) FROM PUBLIC;
        GRANT EXECUTE ON FUNCTION public.approve_web_login_request(uuid) TO authenticated;
        """
    )


def remove_supabase_objects(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    schema_editor.execute(
        """
        DROP TRIGGER IF EXISTS web_login_request_approved_broadcast ON public.web_login_requests;
        DROP FUNCTION IF EXISTS public.notify_web_login_request_approved();
        DROP FUNCTION IF EXISTS public.approve_web_login_request(uuid);
        """
    )


class Migration(migrations.Migration):
    dependencies = [("qr_login", "0001_initial")]

    operations = [migrations.RunPython(create_supabase_objects, remove_supabase_objects)]
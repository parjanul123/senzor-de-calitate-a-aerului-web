from supabase import create_client

client = create_client(
    'https://eakzxbfcwbgfxfujzote.supabase.co',
    'sb_publishable_ofI6pPkeb2csAsw_ZqhCng_d3ADhRZU'
)

try:
    response = client.table('web_login_requests').select('*').limit(1).execute()
    print('✅ Table accessible')
    if response.data:
        print('Columns:', list(response.data[0].keys()))
    else:
        print('No data yet, but table exists')
except Exception as e:
    print(f'❌ Error: {e}')

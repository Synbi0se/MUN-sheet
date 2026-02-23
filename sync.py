import gspread
from google.oauth2.service_account import Credentials
from supabase import create_client
import os

# === TES SHEETS (remplace par tes vrais IDs) ===
SHEETS_IDS = [
    '1ABC...ID_SHEET_1',
    '1DEF...ID_SHEET_2',
    # ajoute tous tes sheets
]
SHEET_NAME = "Sheet1"

# === SUPABASE ===
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def main():
    # 1. Google Sheets
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_info({
        "type": "service_account",
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL")
    }, scopes=scopes)
    
    client = gspread.authorize(creds)
    
    # 2. Fusionner TOUS les sheets
    all_data = []
    for sheet_id in SHEETS_IDS:
        sheet = client.open_by_key(sheet_id).worksheet(SHEET_NAME)
        rows = sheet.get_all_records()
        for row in rows:
            all_data.append({
                "mail": row.get("mail", row.get("email", "")).lower().strip(),
                "committee": row.get("comité", row.get("committee", "")),
                "attrib": row.get("attribution", row.get("attrib", ""))
            })
    
    print(f"📊 Fusion: {len(all_data)} lignes de {len(SHEETS_IDS)} sheets")
    
    # 3. Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table('Attribution 2026').upsert(all_data).execute()
    print(f"✅ {len(all_data)} lignes synchronisées !")

if __name__ == "__main__":
    main()
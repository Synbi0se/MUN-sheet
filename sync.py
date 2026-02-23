import gspread
from google.oauth2.service_account import Credentials
from supabase import create_client
import os

SHEETS_IDS = [
    '1ABC123xyzDEF456ghi...',  # Sheet 1 ID (dans l'URL)
    '1XYZ789uvwRST012klm...'   # Sheet 2 ID (dans l'URL)
]
SHEET_NAME = "chaumun.eu"

def main():
    # Google Sheets
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
    
    # Fusionner les 2 sheets
    all_data = []
    for i, sheet_id in enumerate(SHEETS_IDS, 1):
        print(f"📖 Lecture Sheet {i}: {sheet_id}")
        sheet = client.open_by_key(sheet_id).worksheet(SHEET_NAME)
        rows = sheet.get_all_records()
        
        for row in rows[1:]:  # Skip header
            all_data.append({
                "mail": row.get("mail", row.get("email", "")).lower().strip(),
                "committee": row.get("comité", row.get("committee", row.get("comite", ""))),
                "attrib": row.get("attribution", row.get("attrib", row.get("attribu", "")))
            })
    
    print(f"📊 Fusion: {len(all_data)} lignes de 2 sheets")
    
    # Supabase
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
    response = supabase.table('Attribution 2026').upsert(all_data).execute()
    print(f"✅ {len(all_data)} lignes synchronisées !")
    print(f"Supabase response: {response}")

if __name__ == "__main__":
    main()
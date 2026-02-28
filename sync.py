import gspread
from google.oauth2.service_account import Credentials
from supabase import create_client
import os

SHEETS_IDS = [
    '1j24ofOVLaJgBexKr95yCe8cYch1cz-ApxhjC-GG6i8w',
    '1sGikSRzfWdiD8mNfAbSPMDsy0oyd5tmYX94KvonPTtg',
]
SHEET_NAME = "chaumun.eu"

def main():
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
    L = []
    
    for i, sheet_id in enumerate(SHEETS_IDS, 1):
        print(f"📖 Lecture Sheet {i}: {sheet_id}")
        sheet = client.open_by_key(sheet_id).worksheet(SHEET_NAME)
        rows = sheet.get_all_values()  # Toutes les cellules
        
        for row in rows[1:]:  # Skip header
            # Convertir en string et joindre
            line = ','.join(str(cell) for cell in row) + '\n'
            if (line != ',,\n' and '@' in line and ',,' not in line):
                L.append(line.strip())
    
    print(f"📊 {len(L)} lignes filtrées de {len(SHEETS_IDS)} sheets")
    
    import csv
    import io
    
    all_data = []
    csv_file = io.StringIO()
    for line in L:
        csv_file.write(line + '\n')
    csv_file.seek(0)
    
    reader = csv.DictReader(csv_file)
    for row in reader:
        current_row = str(row)
        if '@' in current_row and "'committee': '', 'attrib': ''}" not in current_row: 
            all_data.append({
                "mail": row.get("mail", "").lower().strip(),
                "committee": row.get("committee", row.get("comité", "")),
                "attrib": row.get("attrib", row.get("attribution", ""))
            })
    
    # Supabase
    try :
        supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
        response = supabase.table('Attribution 2026').upsert(all_data).execute()
        print(f"✅ {len(all_data)} lignes synchronisées !")
    except :
        print("❌ Erreur lors de l'actualisation Supabase.")
    
if __name__ == "__main__":
    main()
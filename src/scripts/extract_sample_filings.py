import os
import shutil
from typing import List

SOURCE_ROOT = "/Users/soheilkhodadadi/DataWork/10-X_C_2021-2124"
DEST_FOLDER = "data/external"
COMPANY_LIST_PATH = "data/metadata/company_lists/company_list.txt"

def load_company_list(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

def find_all_txt_files(root: str) -> List[str]:
    matches = []
    for root_dir, _, files in os.walk(root):
        for file in files:
            if file.endswith(".txt"):
                matches.append(os.path.join(root_dir, file))
    return matches

def extract_company_name_and_cik(file_path: str) -> tuple[str, str]:
    name = ""
    cik = ""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "COMPANY CONFORMED NAME" in line:
                name = line.split(":", 1)[-1].strip().lower()
            if "CENTRAL INDEX KEY" in line:
                cik = line.split(":", 1)[-1].strip()
            if "STATE OF INCORPORATION" in line:  # end of company block
                break
    return name, cik

def main():
    os.makedirs(DEST_FOLDER, exist_ok=True)

    company_targets = load_company_list(COMPANY_LIST_PATH)
    print(f"[✓] Loaded {len(company_targets)} target companies.")

    txt_files = find_all_txt_files(SOURCE_ROOT)
    print(f"[✓] Found {len(txt_files)} total .txt filings to search.")

    match_count = 0
    for file_path in txt_files:
        try:
            name, cik = extract_company_name_and_cik(file_path)
            if any(target in name for target in company_targets):
                filename = os.path.basename(file_path)
                dest_path = os.path.join(DEST_FOLDER, filename)
                shutil.copyfile(file_path, dest_path)
                print(f"[→] Copied: {filename} ({name})")
                match_count += 1
        except Exception as e:
            print(f"[x] Skipped: {file_path} ({str(e)})")

    print(f"\n[✓] Done! {match_count} matching files copied to {DEST_FOLDER}")

if __name__ == "__main__":
    main()

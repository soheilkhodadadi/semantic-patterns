import os
import shutil
import pandas as pd
from typing import List

SOURCE_ROOT = "/Users/soheilkhodadadi/DataWork/10-X_C_2021-2124"
DEST_FOLDER = "data/external"
COMPANY_LIST_PATH = "data/metadata/company_lists/company_list.csv"

def load_target_ciks(path: str) -> List[str]:
    df = pd.read_csv(path)
    return df["CIK"].astype(str).str.zfill(10).tolist()

def find_all_txt_files(root: str) -> List[str]:
    matches = []
    for root_dir, _, files in os.walk(root):
        for file in files:
            if file.endswith(".txt"):
                matches.append(os.path.join(root_dir, file))
    return matches

def extract_cik(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "CENTRAL INDEX KEY" in line:
                return line.split(":", 1)[-1].strip().zfill(10)
    return ""

def main():
    os.makedirs(DEST_FOLDER, exist_ok=True)

    target_ciks = set(load_target_ciks(COMPANY_LIST_PATH))
    print(f"[✓] Loaded {len(target_ciks)} target CIKs.")

    txt_files = find_all_txt_files(SOURCE_ROOT)
    print(f"[✓] Found {len(txt_files)} total .txt filings to search.")

    match_count = 0
    for file_path in txt_files:
        try:
            cik = extract_cik(file_path)
            if cik in target_ciks:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(DEST_FOLDER, filename)
                shutil.copyfile(file_path, dest_path)
                print(f"[→] Copied: {filename} (CIK: {cik})")
                match_count += 1
        except Exception as e:
            print(f"[x] Skipped: {file_path} ({str(e)})")

    print(f"\n[✓] Done! {match_count} matching files copied to {DEST_FOLDER}")

if __name__ == "__main__":
    main()

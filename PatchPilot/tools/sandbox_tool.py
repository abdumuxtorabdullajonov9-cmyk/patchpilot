import os
import shutil
import tempfile
from tools.scanner_tool import scan_repo


def verify_fix(original_repo_path: str, file_relative_path: str, fixed_code: str) -> dict:
    """
    Tuzatilgan kodni vaqtinchalik nusxada sinaydi:
    1. Butun repo'ni vaqtinchalik papkaga nusxalaydi.
    2. Faqat tuzatilgan faylni yangi kod bilan almashtiradi.
    3. Semgrep'ni qayta ishga tushiradi.
    4. Natijani qaytaradi: muvaffaqiyatlimi, qolgan topilmalar soni.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_repo = os.path.join(tmp_dir, "repo")
        shutil.copytree(original_repo_path, tmp_repo)

        target_file = os.path.join(tmp_repo, file_relative_path)
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(fixed_code)

        new_findings = scan_repo(tmp_repo)

        return {
            "success": len(new_findings) == 0,
            "remaining_findings": len(new_findings),
            "details": new_findings,
        }
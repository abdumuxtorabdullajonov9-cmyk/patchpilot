import subprocess
import json
import os


def scan_repo(repo_path: str) -> list[dict]:
    abs_path = os.path.abspath(repo_path)

    result = subprocess.run(
        [
            "docker", "run", "--rm",
            "-v", f"{abs_path}:/src",
            "semgrep/semgrep",
            "semgrep",
            "--config=p/security-audit",
            "--config=p/python",
            "--config=p/secrets",
            "--no-git-ignore",
            "--json", "/src"
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    try:
        data = json.loads(result.stdout)
        return data.get("results", [])
    except json.JSONDecodeError:
        print("JSON o'qishda xato. stderr:")
        print(result.stderr[:1000])
        return []
def debug_scan(repo_path: str):
    abs_path = os.path.abspath(repo_path)
    print("Tekshirilayotgan yo'l:", abs_path)
    print("Bu yo'l mavjudmi:", os.path.exists(abs_path))

    result = subprocess.run(
        [
            "docker", "run", "--rm",
            "-v", f"{abs_path}:/src",
            "semgrep/semgrep",
            "semgrep", "--config=auto", "--no-git-ignore", "--json", "/src"
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    print("\n--- STDOUT (birinchi 3000 belgi) ---")
    print(result.stdout[:3000])
    print("\n--- STDERR (birinchi 3000 belgi) ---")
    print(result.stderr[:3000])
    print("\n--- Qaytish kodi ---")
    print(result.returncode)
def check_mount(repo_path: str):
    """Docker konteyner ichida /src papkasi to'g'ri bog'langanini tekshiradi."""
    abs_path = os.path.abspath(repo_path)
    result = subprocess.run(
        [
            "docker", "run", "--rm",
            "-v", f"{abs_path}:/src",
            "semgrep/semgrep",
            "ls", "-la", "/src"
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    print("--- /src ichidagi fayllar ---")
    print(result.stdout)
    print("--- xatolar (bo'lsa) ---")
    print(result.stderr)
import streamlit as st
import os
import shutil
import tempfile
import subprocess

from tools.scanner_tool import scan_repo
from agents.triage_agent import triage_finding
from agents.fixer_agent import fix_finding
from tools.sandbox_tool import verify_fix
from agents.pr_agent import open_pull_request

st.set_page_config(page_title="PatchPilot", page_icon="🛡️", layout="centered")

st.title("🛡️ PatchPilot")
st.caption("AI agent that finds, fixes, and verifies security vulnerabilities — powered by NVIDIA Nemotron on Nebius Token Factory")

repo_url = st.text_input("GitHub repo URL", placeholder="https://github.com/username/reponame")
run_button = st.button("🔍 Scan & Fix", type="primary")

if run_button and repo_url:
    with tempfile.TemporaryDirectory() as tmp_dir:
        local_path = os.path.join(tmp_dir, "repo")

        status = st.status("Cloning repository...", expanded=True)
        clone_result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, local_path],
            capture_output=True, text=True
        )

        if clone_result.returncode != 0:
            status.update(label="❌ Clone failed", state="error")
            st.error(clone_result.stderr[:500])
            st.stop()

        status.write("✅ Repository cloned.")

        templates_path = os.path.join(local_path, "PatchPilot", "examples", "_templates")
        if os.path.exists(templates_path):
            shutil.rmtree(templates_path)
            status.write("ℹ️ Skipped `_templates/` (benchmark archive, not real code).")

        status.update(label="Scanning for vulnerabilities...")
        findings = scan_repo(local_path)
        status.write(f"Found **{len(findings)}** potential issue(s).")

        if len(findings) == 0:
            status.update(label="✅ No vulnerabilities found!", state="complete")
            st.success("This repository looks clean according to our rules.")
            st.stop()

        files_to_fix = {}
        fixed_count = 0

        for f in findings:
            check_id = f.get("check_id", "unknown")
            path = f.get("path", "")
            status.write(f"🔎 Analyzing `{check_id}` in `{os.path.basename(path)}`...")

            result = triage_finding(f)

            with st.expander(f"{'🔴' if result['is_real_vulnerability'] else '⚪'} {check_id} — {result['severity']}"):
                st.write(result["explanation"])

            if result["is_real_vulnerability"]:
                container_prefix = "/src/"
                if path.startswith(container_prefix):
                    rel_path = path[len(container_prefix):]
                else:
                    rel_path = path.lstrip("/")
                abs_file = os.path.join(local_path, rel_path)

                if abs_file not in files_to_fix:
                    with open(abs_file, "r", encoding="utf-8") as src:
                        files_to_fix[abs_file] = src.read()

                status.write(f"🛠️ Fixing `{check_id}`...")
                files_to_fix[abs_file] = fix_finding(f, files_to_fix[abs_file])
                fixed_count += 1

        if fixed_count == 0:
            status.update(label="No real vulnerabilities confirmed.", state="complete")
            st.info("All findings were classified as false positives.")
            st.stop()

        status.write(f"✅ Applied {fixed_count} fix(es). Verifying in sandbox...")

        all_verified = True
        for abs_file, fixed_code in files_to_fix.items():
            rel_path = os.path.relpath(abs_file, local_path)
            rel_dir = os.path.dirname(rel_path) or "."
            file_name = os.path.basename(rel_path)
            verification = verify_fix(os.path.join(local_path, rel_dir), file_name, fixed_code)
            if not verification["success"]:
                all_verified = False
            else:
                with open(abs_file, "w", encoding="utf-8") as out:
                    out.write(fixed_code)

        if all_verified:
            status.update(label="✅ All fixes verified!", state="complete")
            st.success(f"Fixed and verified {fixed_count} vulnerability(ies).")

            repo_full_name = repo_url.rstrip("/").replace("https://github.com/", "").replace(".git", "")

            try:
                for abs_file, fixed_code in files_to_fix.items():
                    rel_path = os.path.relpath(abs_file, local_path).replace("\\", "/")
                    st.write(f"DEBUG: so'ralayotgan yo'l → `{rel_path}`")  # vaqtincha, keyin olib tashlanadi
                    pr_url = open_pull_request(
                        repo_full_name=repo_full_name,
                        file_relative_path=rel_path,
                        fixed_code=fixed_code,
                    )
                    st.markdown(f"### 🎉 Pull Request created:")
                    st.markdown(f"[{pr_url}]({pr_url})")
            except Exception as e:
                st.warning(f"Fixes verified locally, but PR creation failed: {e}")
        else:
            status.update(label="⚠️ Some fixes could not be fully verified.", state="error")
            st.warning("Partial fix applied, but verification did not fully pass.")
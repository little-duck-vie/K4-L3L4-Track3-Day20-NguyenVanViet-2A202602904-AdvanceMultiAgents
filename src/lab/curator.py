"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import json
import re
from pathlib import Path

from .model import make_model
from .tasks import ROOT, eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file.

    Các bước: nạp run.json + trace.md -> (nếu không có check nào thất bại: in cảnh báo và trả về [] mà KHÔNG gọi LLM)
    -> dựng prompt -> model.invoke(prompt) -> parse_skill_blocks -> validate_skill(text, expected_name=name)
    -> ghi `<out_dir>/<name>/SKILL.md`. Mặc định `out_dir` = <gốc lab>/skills/auto (dùng `ROOT` từ lab.tasks).
    Giữ tối đa `max_skills` skill hợp lệ; skill không hợp lệ bị bỏ qua.
    Prompt chứa, với mỗi check thất bại, TÊN và trường `detail` (lời nhận xét của bot đánh giá: phát biểu quy tắc bị vi phạm)
    cùng phần cuối của vết (trace). Với tác vụ học, `detail` chỉ phát biểu quy tắc, không chứa đáp án.
    Tuyệt đối KHÔNG đưa dữ liệu của tác vụ đánh giá (role == "eval") vào prompt.
    model mặc định: make_model() (lab.model).
    Trả về: danh sách đường dẫn SKILL.md đã ghi.
    """
    results_path = Path(results_dir) / source_condition
    output_path = Path(out_dir) if out_dir is not None else ROOT / "skills" / "auto"
    runs = []

    for run_path in sorted(results_path.glob("*/run.json")):
        run = json.loads(run_path.read_text(encoding="utf-8"))
        if run.get("role") != "learn":
            continue

        failed = [
            {
                "name": str(check.get("name", "")),
                "detail": str(check.get("detail", "")),
            }
            for check in run.get("checks", [])
            if not check.get("passed", False)
        ]
        trace_path = run_path.with_name("trace.md")
        trace = trace_path.read_text(encoding="utf-8")[-6000:] if trace_path.exists() else ""
        runs.append({
            "task": str(run.get("task", run_path.parent.name)),
            "failed": failed,
            "trace": trace,
        })

    if not any(run["failed"] for run in runs):
        print("Warning: no failed checks in learning tasks; no skills were generated.")
        return []

    run_sections = []
    for run in runs:
        failed_lines = "\n".join(
            f"- {check['name']}: {check['detail']}" for check in run["failed"]
        ) or "- None"
        run_sections.append(
            f"## Learning run: {run['task']}\n"
            f"Failed checks and reviewer feedback:\n{failed_lines}\n\n"
            f"End of execution trace:\n{run['trace']}"
        )

    prompt = f"""You write reusable SKILL files for a programming and data-analysis agent.
Below are failed checks, reviewer feedback, and execution traces from LEARNING tasks only.
Find general process failures rather than task-specific answers, and write at most {max_skills} concise skills
that help on NEW tasks of the same broad kinds.

Selection strategy:
- Cover distinct task families. When the evidence includes Python package repair, structured-data analysis,
  and log parsing, prefer one broadly triggered checklist for each family instead of several symptom-specific skills.
- Ignore infrastructure aftermath. A missing output after an aborted or recursion-limited run is not evidence that
  the agent needs generic exception handling; teach the end-to-end workflow that creates and validates the output.
- Combine related technical failures and reviewer RULE feedback into the same family checklist.
- Make each description start with "Use whenever" and name broad observable task signals so the agent will select
  the skill even when a hidden organizational convention is not stated in the user request.

Rules:
- Generalize: do not mention task ids, task-specific input filenames, function names, input columns, or computed answers.
- Organizational conventions explicitly stated in reviewer feedback may be preserved in general form, including
  required output artifacts, schema keys, normalization, ordering, tests, and changelog rules. Do not invent rules.
- Each skill must have YAML frontmatter with `name` (lower-case words separated by hyphens) and `description`
  (one sentence explaining WHEN TO USE IT), followed by no more than 40 lines of imperative instructions.
- Prefer short, imperative, testable checklists: inspect all relevant inputs/specifications, implement robustly,
  then run validation and verify every required output before claiming completion.
- Never mention evaluation tasks or evaluation-only material.
- Use exactly this output format for every skill:
=== SKILL: <name> ===
---
name: <name>
description: <when to use it>
---
<instructions>
=== END ===

{chr(10).join(run_sections)}
"""

    selected_model = model if model is not None else make_model()
    reply = selected_model.invoke(prompt).content
    written = []
    for name, text in parse_skill_blocks(str(reply)):
        if len(written) >= max_skills:
            break
        problems = validate_skill(text, expected_name=name)
        if problems:
            print(f"Skipping invalid skill {name!r}: {', '.join(problems)}")
            continue
        skill_path = output_path / name / "SKILL.md"
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(text.rstrip() + "\n", encoding="utf-8")
        written.append(skill_path)
    return written


if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)

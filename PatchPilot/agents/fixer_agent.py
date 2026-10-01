from agents.llm_client import client, MODEL_ULTRA


def fix_finding(finding: dict, file_content: str) -> str:
    """Nemotron Ultra yordamida zaiflikni tuzatadi va to'liq yangilangan fayl matnini qaytaradi."""

    check_id = finding.get("check_id", "noma'lum")
    message = finding.get("extra", {}).get("message", "")
    line = finding.get("start", {}).get("line", "?")

    prompt = f"""Siz tajribali xavfsizlik muhandisisiz. Quyidagi Python faylida xavfsizlik zaifligi bor.

Qoida: {check_id}
Qator: {line}
Muammo: {message}

To'liq fayl matni:
```python
{file_content}
```

Vazifa: faylni tuzating, faqat aynan shu zaiflikni bartaraf eting, boshqa kodni o'zgartirmang, funksiyalar nomini saqlang.
FAQAT tuzatilgan to'liq Python kodini qaytaring, hech qanday izoh, tushuntirish yoki ```python``` belgilarisiz."""

    resp = client.chat.completions.create(
        model=MODEL_ULTRA,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    fixed_code = resp.choices[0].message.content.strip()

    # Model ba'zan ```python ... ``` bilan o'rab yuborishi mumkin, tozalaymiz
    if fixed_code.startswith("```"):
        lines = fixed_code.split("\n")
        lines = lines[1:] if lines[0].startswith("```") else lines
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        fixed_code = "\n".join(lines)

    return fixed_code
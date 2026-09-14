"""Safe standalone HTML rendering for generated Markdown reports."""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone

import markdown


_EVIDENCE_REF = re.compile(r"\[(ev_[0-9a-f]+)\]")


def _render_evidence_refs(safe_markdown: str) -> str:
    """Use compact numbered citations in the report body and full IDs in the index."""
    index_heading = re.search(r"^##\s+.*证据索引.*$", safe_markdown, flags=re.MULTILINE)
    split_at = index_heading.start() if index_heading else len(safe_markdown)
    report_body, evidence_index = safe_markdown[:split_at], safe_markdown[split_at:]
    citation_numbers: dict[str, int] = {}

    def compact_ref(match: re.Match[str]) -> str:
        evidence_id = match.group(1)
        number = citation_numbers.setdefault(evidence_id, len(citation_numbers) + 1)
        return (
            f'<a class="evidence-ref" href="#{evidence_id}" '
            f'aria-label="证据 {evidence_id}" data-ref="{evidence_id}"><sup>{number}</sup></a>'
        )

    report_body = _EVIDENCE_REF.sub(compact_ref, report_body)
    evidence_index = _EVIDENCE_REF.sub(r"[\1](#\1)", evidence_index)
    return report_body + evidence_index


def render_report_html(raw_markdown: str, *, generated_at: datetime | str | None = None) -> str:
    title_match = re.search(r"^#\s+(.+)$", raw_markdown, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "DeepResearch 报告"

    # Model and Web content is untrusted: render Markdown, but never raw HTML.
    safe_markdown = html.escape(raw_markdown, quote=False)
    safe_markdown = _render_evidence_refs(safe_markdown)
    body = markdown.markdown(
        safe_markdown,
        extensions=["extra", "toc", "sane_lists"],
        extension_configs={"toc": {"permalink": True, "toc_depth": "2-3"}},
        output_format="html5",
    )
    body = re.sub(
        r'<li>(<a href="#(ev_[0-9a-f]+)">)',
        r'<li id="\2">\1',
        body,
    )
    if isinstance(generated_at, str):
        exported_at = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    else:
        exported_at = generated_at or datetime.now(timezone.utc)
    timestamp = exported_at.astimezone().strftime("%Y-%m-%d %H:%M %Z")

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data: https:;">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ --ink:#172033; --muted:#657086; --line:#dce2eb; --paper:#fff; --accent:#3157d5; --soft:#f4f7fc; }}
    * {{ box-sizing:border-box; }} html {{ scroll-behavior:smooth; }}
    body {{ margin:0; color:var(--ink); background:#edf1f7; font:16px/1.78 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }}
    main {{ width:min(980px,calc(100% - 32px)); margin:32px auto; padding:64px 76px; background:var(--paper); border:1px solid var(--line); border-radius:18px; box-shadow:0 18px 50px rgba(31,45,74,.09); }}
    .meta {{ margin:0 0 34px; padding-bottom:18px; border-bottom:1px solid var(--line); color:var(--muted); font-size:13px; }}
    h1,h2,h3 {{ line-height:1.35; letter-spacing:-.02em; scroll-margin-top:24px; }}
    h1 {{ margin:0 0 14px; font-size:36px; }} h2 {{ margin:48px 0 18px; padding-bottom:10px; border-bottom:1px solid var(--line); font-size:25px; }} h3 {{ margin:30px 0 12px; font-size:20px; }}
    p {{ margin:0 0 18px; }} a {{ color:var(--accent); text-decoration:none; overflow-wrap:anywhere; }} a:hover {{ text-decoration:underline; }} a.headerlink {{ margin-left:.4em; color:#aab3c4; font-size:.65em; }}
    .evidence-ref {{ position:relative; display:inline-flex; width:1.45em; height:1.45em; margin:0 .12em; align-items:center; justify-content:center; border:1px solid #b9c8f5; border-radius:999px; background:#edf2ff; color:var(--accent); font-size:10px; font-weight:700; line-height:1; vertical-align:super; overflow:visible; }}
    .evidence-ref:hover {{ background:#dce6ff; text-decoration:none; }} .evidence-ref sup {{ position:static; font-size:inherit; line-height:1; }}
    .evidence-ref::after {{ content:attr(data-ref); position:absolute; z-index:20; left:50%; bottom:calc(100% + 8px); width:max-content; max-width:min(360px,80vw); padding:6px 9px; border-radius:7px; background:#172033; color:#fff; box-shadow:0 6px 20px rgba(23,32,51,.22); font:12px/1.35 ui-monospace,SFMono-Regular,Menlo,monospace; white-space:normal; overflow-wrap:anywhere; opacity:0; visibility:hidden; pointer-events:none; transform:translate(-50%,4px); transition:opacity .15s ease,transform .15s ease,visibility .15s; }}
    .evidence-ref:hover::after,.evidence-ref:focus-visible::after {{ opacity:1; visibility:visible; transform:translate(-50%,0); }}
    ul,ol {{ padding-left:1.45em; }} li {{ margin:.55em 0; }} li:target {{ margin-left:-10px; padding:8px 10px; border-radius:8px; background:#fff3c7; }}
    blockquote {{ margin:22px 0; padding:12px 18px; border-left:4px solid var(--accent); background:var(--soft); color:#45516a; }}
    table {{ width:100%; margin:24px 0; border-collapse:collapse; font-size:14px; }} th,td {{ padding:10px 12px; border:1px solid var(--line); text-align:left; vertical-align:top; }} th {{ background:var(--soft); }}
    code {{ padding:.12em .35em; border-radius:5px; background:var(--soft); font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace; }} pre {{ overflow:auto; padding:18px; border-radius:10px; background:#111827; color:#edf2f7; }} pre code {{ padding:0; background:transparent; color:inherit; }}
    @media (max-width:700px) {{ main {{ width:100%; margin:0; padding:34px 22px; border:0; border-radius:0; }} h1 {{ font-size:29px; }} h2 {{ font-size:22px; }} }}
    @media print {{ body {{ background:#fff; }} main {{ width:auto; margin:0; padding:0; border:0; box-shadow:none; }} a {{ color:inherit; }} h2,h3 {{ break-after:avoid; }} table,blockquote {{ break-inside:avoid; }} }}
  </style>
</head>
<body><main><p class="meta">DeepResearch 报告 · HTML 导出时间：{html.escape(timestamp)}</p>{body}</main></body>
</html>
"""


__all__ = ["render_report_html"]

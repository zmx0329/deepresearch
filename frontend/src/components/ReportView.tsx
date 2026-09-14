import DOMPurify from "dompurify";
import ReactMarkdown from "react-markdown";
import { VERIFICATION_LABELS } from "./stageMeta";
import { Evidence, Report } from "../types/api";
import { API_BASE } from "../api/client";

export function ReportView({ report, evidence, onEvidence }: {report?: Report | null; evidence: Evidence[]; onEvidence: (item: Evidence) => void}) {
  if (!report?.content) return null;
  const sanitized = DOMPurify.sanitize(report.content, { ALLOWED_TAGS: [] });
  return <article className="report-view">
    <div className="report-toolbar">
      <a className="report-export" href={`${API_BASE}/runs/${encodeURIComponent(report.run_id)}/report.html`} download>导出 HTML</a>
    </div>
    <ReactMarkdown components={{
      a: ({href, children}) => {
        const ref = evidence.find((item) => href?.includes(item.evidence_id));
        if (ref) return <CitationBadge item={ref} evidence={evidence} onEvidence={onEvidence} />;
        if (!href || !/^https?:\/\//i.test(href)) return <span>{children}</span>;
        return <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>;
      },
      p: ({children}) => <p>{rewriteCitations(children, evidence, onEvidence)}</p>,
    }}>{sanitized}</ReactMarkdown>
    <div className="verification-row">{report.verification.map((check) => <span key={check.kind} className={check.passed ? "pass" : "fail"}>{check.passed ? "✓" : "!"} {VERIFICATION_LABELS[check.kind] ?? check.kind}</span>)}</div>
  </article>;
}

function rewriteCitations(children: React.ReactNode, evidence: Evidence[], onEvidence: (item: Evidence) => void): React.ReactNode {
  if (typeof children === "string") return splitText(children, evidence, onEvidence, 0);
  return Array.isArray(children) ? children.map((child, index) => typeof child === "string" ? splitText(child, evidence, onEvidence, index) : child) : children;
}

function splitText(text: string, evidence: Evidence[], onEvidence: (item: Evidence) => void, key: number) {
  const tokens = text.split(/(\[(?:\^)?ev_[\w-]+\])/g);
  return tokens.map((token, index) => {
    const id = token.match(/ev_[\w-]+/)?.[0]; const item = evidence.find((entry) => entry.evidence_id === id);
    return item ? <CitationBadge key={`${key}-${index}`} item={item} evidence={evidence} onEvidence={onEvidence} /> : token;
  });
}

function CitationBadge({ item, evidence, onEvidence }: {item: Evidence; evidence: Evidence[]; onEvidence: (item: Evidence) => void}) {
  const number = evidence.findIndex((entry) => entry.evidence_id === item.evidence_id) + 1;
  return <button
    className="citation-link"
    data-ref={item.evidence_id}
    aria-label={`查看证据 ${item.evidence_id}`}
    onClick={() => onEvidence(item)}
  ><sup>{number}</sup></button>;
}

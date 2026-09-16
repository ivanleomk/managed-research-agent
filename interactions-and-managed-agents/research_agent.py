"""Research Agent Pipeline.

Multi-source academic and corporate research engine:
- arXiv: recent preprints, clean abstracts, PDF URLs, code/dataset mentions
- OpenAlex: high-impact works, citation counts, DOI, author affiliations & h-index
- Artifacts: extraction of datasets, benchmarks, and GitHub repos
- SEC EDGAR (optional): company CIK and recent filings for commercial context
- Generates structured Markdown briefing and JSON data.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional

OPENALEX_MAILTO = "ivanleomk@gmail.com"
USER_AGENT = f"ResearchAgent/1.0 (mailto:{OPENALEX_MAILTO})"


@dataclass
class AuthorProfile:
    name: str
    openalex_id: Optional[str] = None
    institution: Optional[str] = None
    position: str = "middle"  # first, middle, last
    h_index: Optional[int] = None
    works_count: Optional[int] = None
    cited_by_count: Optional[int] = None
    profile_url: Optional[str] = None


@dataclass
class PaperItem:
    title: str
    source: str  # "arxiv" or "openalex"
    abstract: str
    authors: List[str]
    published_date: str
    url: str
    doi: Optional[str] = None
    citations: int = 0
    categories: List[str] = field(default_factory=list)
    datasets: List[str] = field(default_factory=list)
    code_urls: List[str] = field(default_factory=list)
    lead_authors: List[AuthorProfile] = field(default_factory=list)


@dataclass
class EdgarFiling:
    form: str
    filing_date: str
    accession_number: str
    primary_doc: str
    url: str


@dataclass
class ResearchReport:
    topic: str
    created_at: str
    papers: List[PaperItem]
    top_collaborators: List[AuthorProfile]
    datasets_discovered: List[str]
    edgar_filings: Optional[List[EdgarFiling]] = None


def make_request(url: str, headers: Optional[Dict[str, str]] = None) -> bytes:
    req_headers = {"User-Agent": USER_AGENT}
    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read()


def extract_datasets_and_code(text: str) -> tuple[List[str], List[str]]:
    if not text:
        return [], []

    code_urls = list(set(re.findall(r"https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", text)))

    known_benchmarks = [
        "MMLU", "GSM8K", "HumanEval", "MATH", "SWE-bench", "ARC", "MBPP",
        "ImageNet", "AlpacaEval", "Chatbot Arena", "LMSYS", "GLUE", "SuperGLUE",
        "SQuAD", "Common Crawl", "FineWeb", "The Pile", "UltraFeedback", "HellaSwag",
        "Spec-Bench", "MT-Bench", "LiveCodeBench", "LongBench", "Needle In A Haystack"
    ]
    detected_datasets = []
    for bench in known_benchmarks:
        if re.search(r"\b" + re.escape(bench) + r"\b", text, re.IGNORECASE):
            detected_datasets.append(bench)

    pattern_matches = re.findall(
        r"\b([A-Z][A-Za-z0-9_-]+(?:\s+[A-Z][A-Za-z0-9_-]+)?)\s+(?:dataset|benchmark|corpus)\b",
        text,
    )
    stop_words = {
        "the", "a", "an", "this", "that", "our", "new", "large", "and", "or",
        "each", "standard", "existing", "synthetic", "public", "private"
    }
    for m in pattern_matches:
        cleaned = m.strip()
        if len(cleaned) <= 2:
            continue
        if cleaned.lower() in stop_words:
            continue
        detected_datasets.append(cleaned)

    unique_datasets = list(dict.fromkeys(detected_datasets))
    return unique_datasets, code_urls


def fetch_arxiv(query: str, max_results: int = 5) -> List[PaperItem]:
    clean_q = query.strip()
    if " " in clean_q and not clean_q.startswith('"'):
        search_expr = f'all:"{clean_q}"'
    else:
        search_expr = f'all:{clean_q}'

    params = {
        "search_query": search_expr,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": str(max_results),
    }
    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    try:
        raw_xml = make_request(url)
    except Exception as e:
        print(f"[!] ArXiv request failed: {e}", file=sys.stderr)
        return []

    root = ET.fromstring(raw_xml)
    atom_ns = "{http://www.w3.org/2005/Atom}"

    results: List[PaperItem] = []
    for entry in root.findall(f"{atom_ns}entry"):
        title_elem = entry.find(f"{atom_ns}title")
        summary_elem = entry.find(f"{atom_ns}summary")
        id_elem = entry.find(f"{atom_ns}id")
        published_elem = entry.find(f"{atom_ns}published")

        title = title_elem.text.strip().replace("\n", " ") if title_elem is not None else ""
        if not title:
            continue

        abstract = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None else ""
        raw_url = id_elem.text.strip() if id_elem is not None else ""
        published = published_elem.text.strip()[:10] if published_elem is not None else ""

        authors = []
        for author_elem in entry.findall(f"{atom_ns}author"):
            name_elem = author_elem.find(f"{atom_ns}name")
            if name_elem is not None and name_elem.text:
                authors.append(name_elem.text.strip())

        categories = []
        for cat_elem in entry.findall(f"{atom_ns}category"):
            term = cat_elem.get("term")
            if term:
                categories.append(term)

        datasets, code_urls = extract_datasets_and_code(f"{title} {abstract}")

        lead_authors = []
        if authors:
            lead_authors.append(AuthorProfile(name=authors[0], position="first"))
        if len(authors) > 1:
            lead_authors.append(AuthorProfile(name=authors[-1], position="last"))

        results.append(
            PaperItem(
                title=title,
                source="arxiv",
                abstract=abstract,
                authors=authors,
                published_date=published,
                url=raw_url,
                categories=categories,
                datasets=datasets,
                code_urls=code_urls,
                lead_authors=lead_authors,
            )
        )

    return results


def fetch_author_stats_by_id(author_openalex_id: str) -> Optional[Dict[str, Any]]:
    if not author_openalex_id:
        return None

    clean_id = author_openalex_id.split("/")[-1]
    url = f"https://api.openalex.org/authors/{clean_id}?mailto={OPENALEX_MAILTO}"
    try:
        raw_json = make_request(url)
        data = json.loads(raw_json.decode("utf-8"))
        summary = data.get("summary_stats", {})
        insts = data.get("last_known_institutions", [])
        primary_inst = insts[0].get("display_name") if insts else None
        return {
            "h_index": summary.get("h_index"),
            "works_count": data.get("works_count"),
            "cited_by_count": data.get("cited_by_count"),
            "institution": primary_inst,
            "profile_url": f"https://openalex.org/{clean_id}",
        }
    except Exception:
        return None


def fetch_author_stats_by_name(author_name: str) -> Optional[Dict[str, Any]]:
    if not author_name:
        return None

    quoted_name = urllib.parse.quote(author_name)
    url = f"https://api.openalex.org/authors?search={quoted_name}&per-page=1&mailto={OPENALEX_MAILTO}"
    try:
        raw_json = make_request(url)
        data = json.loads(raw_json.decode("utf-8"))
        results = data.get("results", [])
        if not results:
            return None

        top_match = results[0]
        summary = top_match.get("summary_stats", {})
        insts = top_match.get("last_known_institutions", [])
        primary_inst = insts[0].get("display_name") if insts else None
        author_id = top_match.get("id")
        return {
            "openalex_id": author_id,
            "h_index": summary.get("h_index"),
            "works_count": top_match.get("works_count"),
            "cited_by_count": top_match.get("cited_by_count"),
            "institution": primary_inst,
            "profile_url": author_id,
        }
    except Exception:
        return None


def fetch_openalex_works(query: str, max_results: int = 5, since_year: int = 2023) -> List[PaperItem]:
    filter_expr = f"title_and_abstract.search:{query},from_publication_date:{since_year}-01-01"
    params = {
        "filter": filter_expr,
        "sort": "cited_by_count:desc",
        "per-page": str(max_results),
        "mailto": OPENALEX_MAILTO,
    }
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    try:
        raw_json = make_request(url)
        data = json.loads(raw_json.decode("utf-8"))
    except Exception as e:
        print(f"[!] OpenAlex request failed: {e}", file=sys.stderr)
        return []

    results_data = data.get("results", [])
    # Fallback to general search if title_and_abstract filter returns empty
    if not results_data:
        fallback_params = {
            "search": query,
            "filter": f"from_publication_date:{since_year}-01-01",
            "sort": "cited_by_count:desc",
            "per-page": str(max_results),
            "mailto": OPENALEX_MAILTO,
        }
        try:
            raw_fallback = make_request("https://api.openalex.org/works?" + urllib.parse.urlencode(fallback_params))
            results_data = json.loads(raw_fallback.decode("utf-8")).get("results", [])
        except Exception:
            results_data = []

    results: List[PaperItem] = []
    for work in results_data:
        title = work.get("title") or ""
        if not title:
            continue

        abstract = ""
        inv_index = work.get("abstract_inverted_index")
        if inv_index:
            word_positions = []
            for word, positions in inv_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort()
            abstract = " ".join(w for _, w in word_positions)

        authors: List[str] = []
        lead_authors: List[AuthorProfile] = []

        authorships = work.get("authorships", [])
        for a in authorships:
            author_obj = a.get("author", {})
            name = author_obj.get("display_name")
            if not name:
                continue
            authors.append(name)

            position = a.get("author_position", "middle")
            insts = a.get("institutions", [])
            primary_inst = insts[0].get("display_name") if insts else None
            author_id = author_obj.get("id")

            if position in ["first", "last"]:
                lead_authors.append(
                    AuthorProfile(
                        name=name,
                        openalex_id=author_id,
                        institution=primary_inst,
                        position=position,
                        profile_url=author_id,
                    )
                )

        published_date = work.get("publication_date") or str(work.get("publication_year") or "")
        landing_url = work.get("doi") or work.get("id")
        citations = work.get("cited_by_count", 0)

        concepts = [c.get("display_name") for c in work.get("concepts", []) if c.get("display_name")]
        datasets, code_urls = extract_datasets_and_code(f"{title} {abstract}")

        results.append(
            PaperItem(
                title=title,
                source="openalex",
                abstract=abstract,
                authors=authors,
                published_date=published_date,
                url=landing_url,
                doi=work.get("doi"),
                citations=citations,
                categories=concepts[:4],
                datasets=datasets,
                code_urls=code_urls,
                lead_authors=lead_authors,
            )
        )

    return results


def fetch_edgar_filings(ticker: str, max_filings: int = 3) -> List[EdgarFiling]:
    headers = {"User-Agent": f"ResearchAgent/1.0 ({OPENALEX_MAILTO})"}
    try:
        tickers_url = "https://www.sec.gov/files/company_tickers.json"
        raw_tickers = make_request(tickers_url, headers=headers)
        data = json.loads(raw_tickers.decode("utf-8"))
    except Exception as e:
        print(f"[!] SEC tickers lookup failed: {e}", file=sys.stderr)
        return []

    cik_str: Optional[str] = None
    for entry in data.values():
        if entry.get("ticker", "").upper() == ticker.upper():
            cik_str = str(entry.get("cik_str")).zfill(10)
            break

    if not cik_str:
        return []

    submissions_url = f"https://data.sec.gov/submissions/CIK{cik_str}.json"
    try:
        raw_sub = make_request(submissions_url, headers=headers)
        sub_data = json.loads(raw_sub.decode("utf-8"))
    except Exception as e:
        print(f"[!] SEC submissions failed: {e}", file=sys.stderr)
        return []

    recent = sub_data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])

    filings: List[EdgarFiling] = []
    cik_raw = str(int(cik_str))
    for i in range(min(len(forms), 30)):
        form = forms[i]
        if form in ["10-K", "10-Q", "8-K"]:
            acc = accessions[i]
            doc = primary_docs[i]
            acc_no_dash = acc.replace("-", "")
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_raw}/{acc_no_dash}/{doc}"
            filings.append(
                EdgarFiling(
                    form=form,
                    filing_date=dates[i],
                    accession_number=acc,
                    primary_doc=doc,
                    url=doc_url,
                )
            )
            if len(filings) >= max_filings:
                break

    return filings


def build_research_report(
    query: str,
    fetch_authors_stats: bool = True,
    ticker: Optional[str] = None,
    max_papers: int = 6,
    since_year: int = 2023,
) -> ResearchReport:
    half = max(1, max_papers // 2)
    arxiv_papers = fetch_arxiv(query, max_results=half + 1)
    openalex_papers = fetch_openalex_works(query, max_results=half + 1, since_year=since_year)

    # Interleave to balance fresh preprints and high citations
    combined_raw: List[PaperItem] = []
    max_len = max(len(arxiv_papers), len(openalex_papers))
    for idx in range(max_len):
        if idx < len(arxiv_papers):
            combined_raw.append(arxiv_papers[idx])
        if idx < len(openalex_papers):
            combined_raw.append(openalex_papers[idx])

    # Deduplicate papers by normalized title
    seen_titles = set()
    combined_papers: List[PaperItem] = []
    for paper in combined_raw:
        norm_title = re.sub(r"\W+", "", paper.title.lower())
        if norm_title in seen_titles:
            continue
        seen_titles.add(norm_title)
        combined_papers.append(paper)
        if len(combined_papers) >= max_papers:
            break

    # Discover datasets
    all_datasets = set()
    for p in combined_papers:
        for d in p.datasets:
            all_datasets.add(d)

    # Discover key collaborators (lead authors)
    collaborator_map: Dict[str, AuthorProfile] = {}
    for p in combined_papers:
        for author in p.lead_authors:
            if author.name not in collaborator_map:
                collaborator_map[author.name] = author

    # Enrich profiles with h-index, works count, and affiliations
    if fetch_authors_stats:
        enriched_count = 0
        for author in collaborator_map.values():
            if enriched_count >= 6:
                break

            stats = None
            if author.openalex_id:
                stats = fetch_author_stats_by_id(author.openalex_id)
            elif author.name:
                stats = fetch_author_stats_by_name(author.name)

            if stats:
                author.h_index = stats.get("h_index")
                author.works_count = stats.get("works_count")
                author.cited_by_count = stats.get("cited_by_count")
                if not author.institution and stats.get("institution"):
                    author.institution = stats.get("institution")
                if not author.profile_url and stats.get("profile_url"):
                    author.profile_url = stats.get("profile_url")
                enriched_count += 1

    edgar_filings = None
    if ticker:
        edgar_filings = fetch_edgar_filings(ticker)

    return ResearchReport(
        topic=query,
        created_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        papers=combined_papers,
        top_collaborators=list(collaborator_map.values())[:6],
        datasets_discovered=sorted(list(all_datasets)),
        edgar_filings=edgar_filings,
    )


def format_markdown_brief(report: ResearchReport, ticker: Optional[str] = None) -> str:
    lines = [
        f"# Research Brief: {report.topic.title()}",
        f"*Generated: {report.created_at}*",
        "",
        "## 1. Executive Summary",
        f"- **Focus Topic:** `{report.topic}`",
        f"- **Total Primary Papers Analyzed:** {len(report.papers)}",
        f"- **Datasets & Benchmarks Identified:** {', '.join(f'`{d}`' for d in report.datasets_discovered) if report.datasets_discovered else 'None explicitly cited'}",
        "",
        "## 2. Key Papers & Findings",
    ]

    for i, paper in enumerate(report.papers, 1):
        lines.append(f"### {i}. [{paper.title}]({paper.url})")
        meta = [f"**Source:** `{paper.source.upper()}`", f"**Date:** {paper.published_date}"]
        if paper.citations > 0:
            meta.append(f"**Citations:** {paper.citations}")
        lines.append(" | ".join(meta))
        lines.append("")

        authors_str = ", ".join(paper.authors[:4])
        if len(paper.authors) > 4:
            authors_str += " et al."
        lines.append(f"- **Authors:** {authors_str}")

        clean_abstract = paper.abstract[:300] + "..." if len(paper.abstract) > 300 else paper.abstract
        if clean_abstract:
            lines.append(f"- **Abstract / Core Idea:** {clean_abstract}")

        if paper.datasets:
            lines.append(f"- **Datasets/Benchmarks:** {', '.join(f'`{d}`' for d in paper.datasets)}")
        if paper.code_urls:
            lines.append(f"- **Code Repo:** {', '.join(f'[{u}]({u})' for u in paper.code_urls)}")
        lines.append("")

    lines.append("## 3. Potential Collaborator Intel")
    lines.append("| Author | Role | Affiliation | Works | Citations | h-index | Profile |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for author in report.top_collaborators:
        role = "Lead (First)" if author.position == "first" else ("PI (Last)" if author.position == "last" else "Co-author")
        inst = author.institution or "N/A"
        works = str(author.works_count) if author.works_count is not None else "-"
        cites = str(author.cited_by_count) if author.cited_by_count is not None else "-"
        h = str(author.h_index) if author.h_index is not None else "-"
        profile = f"[OpenAlex]({author.profile_url})" if author.profile_url else "-"
        lines.append(f"| **{author.name}** | {role} | {inst} | {works} | {cites} | {h} | {profile} |")
    lines.append("")

    if report.edgar_filings:
        ticker_label = ticker.upper() if ticker else "CORP"
        lines.append(f"## 4. Corporate Cross-Reference (SEC EDGAR: {ticker_label})")
        lines.append("| Form | Date | Accession | Link |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for f in report.edgar_filings:
            lines.append(f"| **{f.form}** | {f.filing_date} | `{f.accession_number}` | [View Filing]({f.url}) |")
        lines.append("")

    lines.append("## 5. Next Steps")
    lines.append("- Deep dive on first-author recent preprints.")
    lines.append("- Audit evaluation consistency on identified benchmarks.")
    lines.append("- Track citation velocity of lead researchers.")

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Multi-source Academic & Corporate Research Agent")
    parser.add_argument("--query", "-q", required=True, help="Topic or query to research")
    parser.add_argument("--ticker", "-t", default=None, help="Optional stock ticker for EDGAR filings")
    parser.add_argument("--max-papers", "-n", type=int, default=6, help="Number of papers to retrieve")
    parser.add_argument("--since-year", "-s", type=int, default=2023, help="Earliest publication year for works")
    parser.add_argument("--out-dir", "-o", default="out", help="Output directory for reports")
    parser.add_argument("--no-enrich", action="store_true", help="Skip deep author metric lookups")

    args = parser.parse_args()

    print(f"[*] Researching topic: '{args.query}'...")
    report = build_research_report(
        query=args.query,
        fetch_authors_stats=not args.no_enrich,
        ticker=args.ticker,
        max_papers=args.max_papers,
        since_year=args.since_year,
    )

    out_path = Path(args.out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    slug = re.sub(r"\W+", "-", args.query.lower()).strip("-")
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    md_content = format_markdown_brief(report, ticker=args.ticker)
    md_file = out_path / f"brief-{date_str}-{slug}.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    json_file = out_path / f"brief-{date_str}-{slug}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        report_dict = asdict(report)
        json.dump(report_dict, f, indent=2)

    print(f"[✓] Markdown brief saved to: {md_file}")
    print(f"[✓] Raw structured data saved to: {json_file}")


if __name__ == "__main__":
    main()

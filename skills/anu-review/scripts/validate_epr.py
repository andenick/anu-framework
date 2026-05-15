#!/usr/bin/env python3
"""
validate_epr.py - EPR (Extension Provenance Record) Validation Module

Part of the Anu Review tool suite.
Validates EPR files for completeness and compliance with Anu Extension Standard v1.0.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class EPRValidationResult:
    """Result of validating a single EPR file."""
    series_id: str
    file_exists: bool
    agent_understanding: bool
    book_context: bool
    original_methodology: bool
    current_methodology: bool
    methodology_changes: bool
    transition_analysis: bool
    faithfulness_score: Optional[float]
    certification_status: Optional[str]
    score: float
    issues: List[str]


def extract_faithfulness_score(content: str) -> Optional[float]:
    """Extract faithfulness score from EPR content."""
    match = re.search(r"Faithfulness.*?(\d{1,3})%", content, re.IGNORECASE)
    if match:
        return float(match.group(1)) / 100
    return None


def extract_certification_status(content: str) -> Optional[str]:
    """Extract certification status from EPR content."""
    if re.search(r"CERTIFIED WITH NOTES", content, re.IGNORECASE):
        return "CERTIFIED WITH NOTES"
    elif re.search(r"CERTIFIED", content, re.IGNORECASE):
        return "CERTIFIED"
    elif re.search(r"NOT CERTIFIED", content, re.IGNORECASE):
        return "NOT CERTIFIED"
    return None


def validate_epr_file(epr_path: Path) -> EPRValidationResult:
    """
    Validate a single EPR file for completeness.
    
    Args:
        epr_path: Path to the EPR markdown file
        
    Returns:
        EPRValidationResult with scores and issues
    """
    series_id = epr_path.stem.replace("_EPR", "")
    issues = []
    
    # Check file existence
    if not epr_path.exists():
        return EPRValidationResult(
            series_id=series_id,
            file_exists=False,
            agent_understanding=False,
            book_context=False,
            original_methodology=False,
            current_methodology=False,
            methodology_changes=False,
            transition_analysis=False,
            faithfulness_score=None,
            certification_status=None,
            score=0.0,
            issues=["EPR file does not exist"]
        )
    
    # Read file content
    try:
        content = epr_path.read_text(encoding='utf-8')
    except Exception as e:
        return EPRValidationResult(
            series_id=series_id,
            file_exists=True,
            agent_understanding=False,
            book_context=False,
            original_methodology=False,
            current_methodology=False,
            methodology_changes=False,
            transition_analysis=False,
            faithfulness_score=None,
            certification_status=None,
            score=0.0,
            issues=[f"Error reading file: {e}"]
        )
    
    # Check for required sections
    agent_understanding = bool(re.search(
        r"##\s*(Agent Understanding|Understanding Statement)|I understand",
        content, re.IGNORECASE
    ))
    if not agent_understanding:
        issues.append("Missing agent understanding statement")
    
    book_context = bool(re.search(
        r"##\s*Book Context|>\s*[\"'].+[\"']|Shaikh.*quote",
        content, re.IGNORECASE
    ))
    if not book_context:
        issues.append("Missing book context with quotes")
    
    original_methodology = bool(re.search(
        r"##\s*Original Methodology|original.*method|Shaikh.*construct",
        content, re.IGNORECASE
    ))
    if not original_methodology:
        issues.append("Missing original methodology documentation")
    
    current_methodology = bool(re.search(
        r"##\s*Current Methodology|current.*method|extension.*method",
        content, re.IGNORECASE
    ))
    if not current_methodology:
        issues.append("Missing current methodology documentation")
    
    methodology_changes = bool(re.search(
        r"##\s*(Methodology Changes|Changes Assessment)|change.*methodology",
        content, re.IGNORECASE
    ))
    if not methodology_changes:
        issues.append("Missing methodology changes assessment")
    
    transition_analysis = bool(re.search(
        r"##\s*Transition|splice|connection.*ratio|overlap",
        content, re.IGNORECASE
    ))
    if not transition_analysis:
        issues.append("Missing transition analysis")
    
    # Extract scores
    faithfulness_score = extract_faithfulness_score(content)
    certification_status = extract_certification_status(content)
    
    if faithfulness_score is None:
        issues.append("No faithfulness score found")
    if certification_status is None:
        issues.append("No certification status found")
    
    # Calculate score (weighted)
    score_items = [
        (agent_understanding, 0.15),
        (book_context, 0.15),
        (original_methodology, 0.15),
        (current_methodology, 0.15),
        (methodology_changes, 0.10),
        (transition_analysis, 0.15),
        (faithfulness_score is not None, 0.10),
        (certification_status is not None, 0.05),
    ]
    score = sum(weight for present, weight in score_items if present)
    
    return EPRValidationResult(
        series_id=series_id,
        file_exists=True,
        agent_understanding=agent_understanding,
        book_context=book_context,
        original_methodology=original_methodology,
        current_methodology=current_methodology,
        methodology_changes=methodology_changes,
        transition_analysis=transition_analysis,
        faithfulness_score=faithfulness_score,
        certification_status=certification_status,
        score=score,
        issues=issues
    )


def validate_chapter_eprs(
    docs_dir: Path,
    series_ids: List[str],
    extended_series: Optional[List[str]] = None
) -> Tuple[float, List[EPRValidationResult]]:
    """
    Validate all EPR files for a chapter.
    
    Args:
        docs_dir: Path to docs/series directory
        series_ids: List of all series IDs in chapter
        extended_series: List of series that should have EPRs (if None, checks all)
        
    Returns:
        Tuple of (overall_score, list of individual results)
    """
    # If extended_series not specified, check all
    check_series = extended_series if extended_series else series_ids
    
    results = []
    for series_id in check_series:
        epr_path = docs_dir / f"{series_id}_EPR.md"
        result = validate_epr_file(epr_path)
        results.append(result)
    
    # Calculate overall score
    if not results:
        return 1.0, results  # No EPRs needed = 100%
    
    # Only count existing files for score
    existing_results = [r for r in results if r.file_exists]
    if not existing_results:
        # Count existence rate
        return len([r for r in results if r.file_exists]) / len(results), results
    
    total_score = sum(r.score for r in existing_results) / len(existing_results)
    existence_rate = len(existing_results) / len(results)
    
    # Weight: 60% completeness of existing, 40% existence rate
    return (total_score * 0.6) + (existence_rate * 0.4), results


def format_epr_report(results: List[EPRValidationResult]) -> str:
    """Format EPR validation results as a report section."""
    lines = ["## EPR Completeness Analysis\n"]
    
    # Summary table
    lines.append("| Series | Exists | Agent | Context | Orig Method | Curr Method | Changes | Transition | Faith. | Status |")
    lines.append("|--------|--------|-------|---------|-------------|-------------|---------|------------|--------|--------|")
    
    for r in results:
        check = lambda x: "✓" if x else "✗"
        faith = f"{r.faithfulness_score:.0%}" if r.faithfulness_score else "N/A"
        status = r.certification_status[:4] if r.certification_status else "N/A"
        lines.append(
            f"| {r.series_id} | {check(r.file_exists)} | {check(r.agent_understanding)} | "
            f"{check(r.book_context)} | {check(r.original_methodology)} | "
            f"{check(r.current_methodology)} | {check(r.methodology_changes)} | "
            f"{check(r.transition_analysis)} | {faith} | {status} |"
        )
    
    # Issues section
    all_issues = [(r.series_id, issue) for r in results for issue in r.issues if r.file_exists]
    if all_issues:
        lines.append("\n### Issues Found\n")
        for series_id, issue in all_issues:
            lines.append(f"- **{series_id}**: {issue}")
    
    # Missing EPRs
    missing = [r.series_id for r in results if not r.file_exists]
    if missing:
        lines.append(f"\n### Missing EPR Files\n")
        lines.append(f"The following series do not have EPR files: {', '.join(missing)}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: validate_epr.py <docs_dir> <series_id1> [series_id2] ...")
        sys.exit(1)
    
    docs_dir = Path(sys.argv[1])
    series_ids = sys.argv[2:]
    
    score, results = validate_chapter_eprs(docs_dir, series_ids)
    print(f"\nOverall EPR Score: {score:.0%}")
    print(format_epr_report(results))

#!/usr/bin/env python3
"""
run_review.py - Main Anu Review Orchestrator

Part of the Anu Review tool suite.
Runs comprehensive integration quality review for a chapter or project.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

# Import validation modules
from validate_dpr import validate_chapter_dprs, format_dpr_report
from validate_epr import validate_chapter_eprs, format_epr_report


@dataclass
class DimensionScore:
    """Score for a single review dimension."""
    name: str
    weight: float
    score: float
    max_score: float = 1.0
    details: str = ""
    issues: List[str] = field(default_factory=list)
    
    @property
    def weighted_score(self) -> float:
        return self.score * self.weight
    
    @property
    def percentage(self) -> float:
        return (self.score / self.max_score) * 100 if self.max_score > 0 else 0


@dataclass
class ChapterReview:
    """Complete review results for a chapter."""
    chapter_number: int
    chapter_title: str
    series_ids: List[str]
    series_count: int
    dimensions: Dict[str, DimensionScore]
    overall_score: float
    certification_level: str
    gaps: List[str]
    action_items: List[Tuple[str, str]]  # (priority, action)
    timestamp: str


def get_certification_level(score: float) -> str:
    """Determine certification level based on score."""
    if score >= 0.95:
        return "EXEMPLARY"
    elif score >= 0.85:
        return "COMPLETE"
    elif score >= 0.70:
        return "ADEQUATE"
    else:
        return "INCOMPLETE"


def check_data_file_integrity(
    data_dir: Path,
    chapter_num: int,
    series_ids: List[str]
) -> DimensionScore:
    """Check data file integrity for a chapter."""
    issues = []
    score_components = []
    
    # Check main data file
    main_csv = data_dir / f"chapter_{chapter_num:02d}_data.csv"
    main_csv_alt = data_dir / f"chapter_{chapter_num}_data.csv"
    
    main_exists = main_csv.exists() or main_csv_alt.exists()
    score_components.append(1.0 if main_exists else 0.0)
    if not main_exists:
        issues.append(f"Missing chapter_{chapter_num}_data.csv")
    
    # Check extended data file
    ext_csv = data_dir / f"chapter_{chapter_num:02d}_extended.csv"
    ext_csv_alt = data_dir / f"chapter_{chapter_num}_extended.csv"
    
    ext_exists = ext_csv.exists() or ext_csv_alt.exists()
    score_components.append(1.0 if ext_exists else 0.5)  # Extended is optional
    if not ext_exists:
        issues.append(f"Missing chapter_{chapter_num}_extended.csv (may be acceptable)")
    
    # Calculate score
    avg_score = sum(score_components) / len(score_components) if score_components else 0
    
    return DimensionScore(
        name="Data File Integrity",
        weight=0.15,
        score=avg_score,
        details=f"Main CSV: {'✓' if main_exists else '✗'}, Extended CSV: {'✓' if ext_exists else '✗'}",
        issues=issues
    )


def check_series_mapping(
    data_loader_path: Path,
    chapter_num: int,
    series_ids: List[str]
) -> DimensionScore:
    """Check series mapping completeness in data_loader.R."""
    issues = []
    
    if not data_loader_path.exists():
        return DimensionScore(
            name="Series Mapping",
            weight=0.15,
            score=0.0,
            details="data_loader.R not found",
            issues=["data_loader.R file not found"]
        )
    
    content = data_loader_path.read_text(encoding='utf-8')
    
    # Check if CH[X]_SERIES_MAPPING exists
    mapping_pattern = f"CH{chapter_num}_SERIES_MAPPING"
    mapping_exists = mapping_pattern in content
    
    if not mapping_exists:
        return DimensionScore(
            name="Series Mapping",
            weight=0.15,
            score=0.0,
            details=f"{mapping_pattern} not found",
            issues=[f"{mapping_pattern} not defined in data_loader.R"]
        )
    
    # Check each series is in the mapping
    series_found = 0
    for series_id in series_ids:
        if re.search(rf'{series_id}\s*=\s*list\(', content):
            series_found += 1
        else:
            issues.append(f"{series_id} not found in mapping")
    
    score = series_found / len(series_ids) if series_ids else 1.0
    
    return DimensionScore(
        name="Series Mapping",
        weight=0.15,
        score=score,
        details=f"{series_found}/{len(series_ids)} series mapped",
        issues=issues
    )


def check_chart_builders(
    chart_builder_path: Path,
    chapter_num: int
) -> DimensionScore:
    """Check chart builder integration."""
    issues = []
    
    if not chart_builder_path.exists():
        return DimensionScore(
            name="Chart Builder Integration",
            weight=0.10,
            score=0.0,
            details="chart_builder.R not found",
            issues=["chart_builder.R file not found"]
        )
    
    content = chart_builder_path.read_text(encoding='utf-8')
    
    # Check for chapter-specific helper function
    helper_pattern = f"is_chapter{chapter_num}_series"
    has_helper = helper_pattern in content
    
    # Check for specialized builders (varies by chapter)
    has_builders = bool(re.search(rf"build_.*chapter.*{chapter_num}|CHAPTER.*{chapter_num}", content, re.IGNORECASE))
    
    # Calculate score
    score_parts = [
        1.0 if has_helper else 0.5,  # Helper function
        1.0 if has_builders else 0.7,  # Specialized builders (optional)
    ]
    score = sum(score_parts) / len(score_parts)
    
    if not has_helper:
        issues.append(f"Missing {helper_pattern} function")
    
    return DimensionScore(
        name="Chart Builder Integration",
        weight=0.10,
        score=score,
        details=f"Helper: {'✓' if has_helper else '✗'}, Specialized: {'✓' if has_builders else 'generic'}",
        issues=issues
    )


def check_test_coverage(
    tests_dir: Path,
    chapter_num: int
) -> DimensionScore:
    """Check test coverage for a chapter."""
    issues = []
    
    test_file = tests_dir / f"test_chapter_{chapter_num:02d}.R"
    test_file_alt = tests_dir / f"test_chapter_{chapter_num}.R"
    
    test_path = test_file if test_file.exists() else (test_file_alt if test_file_alt.exists() else None)
    
    if not test_path:
        return DimensionScore(
            name="Test Coverage",
            weight=0.10,
            score=0.0,
            details="Test file not found",
            issues=[f"Missing test_chapter_{chapter_num:02d}.R"]
        )
    
    content = test_path.read_text(encoding='utf-8')
    
    # Check for required test sections
    required_tests = [
        ("CHAPTER_METADATA", r"CHAPTER_METADATA"),
        ("Series Mapping", r"SERIES_MAPPING"),
        ("Data Files", r"data.*csv|file\.exists"),
        ("DPR Files", r"DPR|dpr_path"),
        ("EPR Files", r"EPR|epr_path"),
        ("Figure Catalog", r"figure.*catalog|FIGURE"),
    ]
    
    tests_found = 0
    for test_name, pattern in required_tests:
        if re.search(pattern, content, re.IGNORECASE):
            tests_found += 1
        else:
            issues.append(f"Missing tests for: {test_name}")
    
    score = tests_found / len(required_tests)
    
    return DimensionScore(
        name="Test Coverage",
        weight=0.10,
        score=score,
        details=f"{tests_found}/{len(required_tests)} test sections present",
        issues=issues
    )


def check_catalog_consistency(
    catalog_path: Path,
    chapter_num: int,
    series_ids: List[str]
) -> DimensionScore:
    """Check figure catalog consistency."""
    issues = []
    
    if not catalog_path.exists():
        return DimensionScore(
            name="Catalog Consistency",
            weight=0.10,
            score=0.0,
            details="FIGURE_SERIES_CATALOG.json not found",
            issues=["Catalog file not found"]
        )
    
    try:
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
    except Exception as e:
        return DimensionScore(
            name="Catalog Consistency",
            weight=0.10,
            score=0.0,
            details=f"Error reading catalog: {e}",
            issues=[f"Error reading catalog: {e}"]
        )
    
    # Find figures for this chapter
    chapter_figures = [
        (fig_id, fig_data)
        for fig_id, fig_data in catalog.items()
        if fig_data.get("chapter") == chapter_num
    ]
    
    if not chapter_figures:
        return DimensionScore(
            name="Catalog Consistency",
            weight=0.10,
            score=0.5,
            details="No figures found for chapter",
            issues=["No figures assigned to this chapter in catalog"]
        )
    
    # Check each figure
    correct_figures = 0
    for fig_id, fig_data in chapter_figures:
        has_series = bool(fig_data.get("series_ids"))
        has_description = bool(fig_data.get("description"))
        
        if has_series and has_description:
            correct_figures += 1
        else:
            if not has_series:
                issues.append(f"{fig_id}: missing series_ids")
            if not has_description:
                issues.append(f"{fig_id}: missing description")
    
    score = correct_figures / len(chapter_figures) if chapter_figures else 0
    
    return DimensionScore(
        name="Catalog Consistency",
        weight=0.10,
        score=score,
        details=f"{correct_figures}/{len(chapter_figures)} figures complete",
        issues=issues
    )


def check_knowledge_base(
    docs_dir: Path,
    series_ids: List[str]
) -> DimensionScore:
    """Check knowledge base integration (web research, quotes)."""
    issues = []
    total_score = 0
    
    for series_id in series_ids:
        dpr_path = docs_dir / f"{series_id}_DPR.md"
        if not dpr_path.exists():
            continue
            
        content = dpr_path.read_text(encoding='utf-8')
        
        # Check for web research indicators
        has_urls = bool(re.search(r'https?://', content))
        has_quotes = bool(re.search(r'>\s*["\'].+["\']', content))
        has_sources = bool(re.search(r'source|Source|SOURCE', content))
        
        series_score = (has_urls + has_quotes + has_sources) / 3
        total_score += series_score
    
    avg_score = total_score / len(series_ids) if series_ids else 0
    
    if avg_score < 0.7:
        issues.append("Incomplete web research or source documentation")
    
    return DimensionScore(
        name="Knowledge Base Integration",
        weight=0.10,
        score=avg_score,
        details=f"Average documentation: {avg_score:.0%}",
        issues=issues
    )


def run_chapter_review(
    chapter_num: int,
    project_root: Path,
    chapter_title: str = "",
    series_ids: Optional[List[str]] = None
) -> ChapterReview:
    """
    Run a complete review for a chapter.
    
    Args:
        chapter_num: Chapter number to review
        project_root: Root path of the project
        chapter_title: Title of the chapter
        series_ids: List of series IDs (if None, will attempt to detect)
    """
    # Set up paths
    shiny_app_root = project_root / "Technical" / "ShinyApp"
    anu_app_root = project_root / "Technical" / "AnuShinyApp"
    docs_dir = shiny_app_root / "docs" / "series"
    data_dir = shiny_app_root / "data" / "ShaikhAbsorbed"
    catalog_path = data_dir / "catalogs" / "FIGURE_SERIES_CATALOG.json"
    data_loader_path = anu_app_root / "R" / "data_loader.R"
    chart_builder_path = anu_app_root / "R" / "chart_builder.R"
    tests_dir = anu_app_root / "tests"
    
    # If no series_ids provided, use empty list
    if series_ids is None:
        series_ids = []
    
    dimensions = {}
    
    # 1. DPR Completeness
    if series_ids:
        dpr_score, dpr_results = validate_chapter_dprs(docs_dir, series_ids)
        dimensions["dpr"] = DimensionScore(
            name="DPR Completeness",
            weight=0.15,
            score=dpr_score,
            details=f"{sum(1 for r in dpr_results if r.file_exists)}/{len(series_ids)} DPRs exist",
            issues=[issue for r in dpr_results for issue in r.issues]
        )
    else:
        dimensions["dpr"] = DimensionScore(name="DPR Completeness", weight=0.15, score=0, issues=["No series IDs provided"])
    
    # 2. EPR Completeness
    if series_ids:
        epr_score, epr_results = validate_chapter_eprs(docs_dir, series_ids)
        dimensions["epr"] = DimensionScore(
            name="EPR Completeness",
            weight=0.15,
            score=epr_score,
            details=f"{sum(1 for r in epr_results if r.file_exists)}/{len(series_ids)} EPRs exist",
            issues=[issue for r in epr_results for issue in r.issues]
        )
    else:
        dimensions["epr"] = DimensionScore(name="EPR Completeness", weight=0.15, score=0, issues=["No series IDs provided"])
    
    # 3. Data File Integrity
    dimensions["data"] = check_data_file_integrity(data_dir, chapter_num, series_ids)
    
    # 4. Series Mapping
    dimensions["mapping"] = check_series_mapping(data_loader_path, chapter_num, series_ids)
    
    # 5. Chart Builder Integration
    dimensions["charts"] = check_chart_builders(chart_builder_path, chapter_num)
    
    # 6. Test Coverage
    dimensions["tests"] = check_test_coverage(tests_dir, chapter_num)
    
    # 7. Catalog Consistency
    dimensions["catalog"] = check_catalog_consistency(catalog_path, chapter_num, series_ids)
    
    # 8. Knowledge Base Integration
    dimensions["knowledge"] = check_knowledge_base(docs_dir, series_ids)
    
    # Calculate overall score
    overall_score = sum(d.weighted_score for d in dimensions.values())
    certification_level = get_certification_level(overall_score)
    
    # Collect gaps
    gaps = []
    for dim in dimensions.values():
        gaps.extend(dim.issues)
    
    # Generate action items
    action_items = []
    for dim in dimensions.values():
        if dim.score < 0.7:
            priority = "HIGH" if dim.weight >= 0.15 else "MED"
            action_items.append((priority, f"Address {dim.name}: {dim.details}"))
        elif dim.score < 0.9:
            action_items.append(("LOW", f"Improve {dim.name}: {dim.details}"))
    
    return ChapterReview(
        chapter_number=chapter_num,
        chapter_title=chapter_title,
        series_ids=series_ids,
        series_count=len(series_ids),
        dimensions=dimensions,
        overall_score=overall_score,
        certification_level=certification_level,
        gaps=gaps,
        action_items=action_items,
        timestamp=datetime.now().isoformat()
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Anu Review for a chapter")
    parser.add_argument("chapter", type=int, help="Chapter number to review")
    parser.add_argument("--project", type=str, default=".", help="Project root path")
    parser.add_argument("--title", type=str, default="", help="Chapter title")
    parser.add_argument("--series", type=str, nargs="+", help="Series IDs to check")
    
    args = parser.parse_args()
    
    project_root = Path(args.project)
    review = run_chapter_review(
        chapter_num=args.chapter,
        project_root=project_root,
        chapter_title=args.title,
        series_ids=args.series
    )
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"  ANU REVIEW: Chapter {review.chapter_number}")
    print(f"{'='*60}")
    print(f"  Score: {review.overall_score:.0%}")
    print(f"  Status: {review.certification_level}")
    print(f"  Series: {review.series_count}")
    print(f"{'='*60}")
    
    print("\nDimension Scores:")
    for dim in review.dimensions.values():
        print(f"  {dim.name}: {dim.score:.0%} ({dim.details})")
    
    if review.action_items:
        print("\nAction Items:")
        for priority, action in review.action_items:
            print(f"  [{priority}] {action}")

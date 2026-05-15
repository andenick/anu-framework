#!/usr/bin/env python3
"""
Anu Extension Standard - Extension Compliance Validator

Validates data series extensions against the Anu Extension Standard v1.0.
Checks for proper documentation, transition quality, and certification requirements.

Usage:
    python validate_extension.py <project_path> [--series SERIES_ID] [--verbose] [--json]

Examples:
    python validate_extension.py /path/to/project
    python validate_extension.py /path/to/project --series S001
    python validate_extension.py /path/to/project --verbose --json > report.json
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


# Anu Extension Standard version
ANU_EXTENSION_VERSION = "1.0"

# Transition metric thresholds
TRANSITION_THRESHOLDS = {
    "connection_ratio": {"pass": (0.97, 1.03), "warn": (0.95, 1.05)},
    "growth_rate_continuity": {"pass": 0.03, "warn": 0.05},
    "trend_alignment": {"pass": 0.98, "warn": 0.95},
    "level_difference": {"pass": 0.01, "warn": 0.03}
}

# Faithfulness score weights
FAITHFULNESS_WEIGHTS = {
    "methodology_match": 0.30,
    "source_match": 0.20,
    "transformation_replication": 0.20,
    "transition_quality": 0.20,
    "documentation_completeness": 0.10
}

# Component minimums for certification
COMPONENT_MINIMUMS = {
    "methodology_match": 0.70,
    "source_match": 0.80,
    "transformation_replication": 0.75,
    "transition_quality": 0.70,
    "documentation_completeness": 0.90
}


class ExtensionValidator:
    """Validates extensions against Anu Extension Standard."""
    
    def __init__(self, project_path: str, verbose: bool = False):
        self.project_path = Path(project_path)
        self.verbose = verbose
        self.results: Dict[str, Any] = {
            "anu_extension_version": ANU_EXTENSION_VERSION,
            "validation_date": datetime.now().isoformat(),
            "project_path": str(project_path),
            "series_validated": [],
            "overall_status": "UNKNOWN",
            "issues": [],
            "warnings": []
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def validate_all(self) -> Dict[str, Any]:
        """Validate all extensions in the project."""
        self.log("Starting Anu Extension Standard validation...")
        
        # Find all EPR files
        epr_files = self._find_epr_files()
        
        if not epr_files:
            self.results["issues"].append({
                "code": "EXT_NO_EPR_FILES",
                "message": "No EPR files found in project",
                "severity": "WARNING"
            })
            self.results["overall_status"] = "NO_EXTENSIONS"
            return self.results
        
        # Validate each EPR file
        for epr_path in epr_files:
            series_result = self._validate_series(epr_path)
            self.results["series_validated"].append(series_result)
        
        # Calculate overall status
        self._calculate_overall_status()
        
        return self.results
    
    def validate_series(self, series_id: str) -> Dict[str, Any]:
        """Validate a specific series extension."""
        self.log(f"Validating series {series_id}...")
        
        # Find EPR file for series
        epr_path = self._find_series_epr(series_id)
        
        if not epr_path:
            self.results["issues"].append({
                "code": "EXT_NO_EPR",
                "message": f"No EPR file found for series {series_id}",
                "severity": "ERROR"
            })
            self.results["overall_status"] = "FAILED"
            return self.results
        
        series_result = self._validate_series(epr_path)
        self.results["series_validated"].append(series_result)
        self._calculate_overall_status()
        
        return self.results
    
    def _find_epr_files(self) -> List[Path]:
        """Find all EPR files in the project."""
        epr_files = []
        
        # Search common locations
        search_paths = [
            self.project_path / "Technical" / "ShinyApp" / "docs" / "series",
            self.project_path / "Technical" / "docs" / "series",
            self.project_path / "docs" / "series"
        ]
        
        for search_path in search_paths:
            if search_path.exists():
                epr_files.extend(search_path.glob("*_EPR.md"))
        
        # Also search recursively for any EPR files
        epr_files.extend(self.project_path.rglob("*_EPR.md"))
        
        # Deduplicate
        epr_files = list(set(epr_files))
        
        self.log(f"Found {len(epr_files)} EPR files")
        return epr_files
    
    def _find_series_epr(self, series_id: str) -> Optional[Path]:
        """Find EPR file for a specific series."""
        epr_files = self._find_epr_files()
        
        for epr_path in epr_files:
            if series_id in epr_path.name:
                return epr_path
        
        return None
    
    def _validate_series(self, epr_path: Path) -> Dict[str, Any]:
        """Validate a single series extension from its EPR file."""
        series_id = self._extract_series_id(epr_path)
        self.log(f"Validating {series_id} from {epr_path}")
        
        result = {
            "series_id": series_id,
            "epr_file": str(epr_path),
            "status": "UNKNOWN",
            "checks": {},
            "issues": [],
            "warnings": []
        }
        
        # Read EPR file
        try:
            epr_content = epr_path.read_text(encoding='utf-8')
        except Exception as e:
            result["issues"].append({
                "code": "EXT_READ_ERROR",
                "message": f"Cannot read EPR file: {str(e)}"
            })
            result["status"] = "FAILED"
            return result
        
        # Run validation checks
        result["checks"]["documentation"] = self._check_documentation(epr_content)
        result["checks"]["agent_understanding"] = self._check_agent_understanding(epr_content)
        result["checks"]["book_context"] = self._check_book_context(epr_content)
        result["checks"]["methodology"] = self._check_methodology(epr_content)
        result["checks"]["transformation"] = self._check_transformation(epr_content)
        result["checks"]["transition"] = self._check_transition(epr_content)
        result["checks"]["certification"] = self._check_certification(epr_content)
        
        # Collect issues and warnings
        for check_name, check_result in result["checks"].items():
            result["issues"].extend(check_result.get("issues", []))
            result["warnings"].extend(check_result.get("warnings", []))
        
        # Determine overall status
        has_critical = any(i.get("severity") == "CRITICAL" for i in result["issues"])
        has_errors = any(i.get("severity") == "ERROR" for i in result["issues"])
        has_warnings = len(result["warnings"]) > 0
        
        if has_critical:
            result["status"] = "FAILED"
        elif has_errors:
            result["status"] = "ISSUES"
        elif has_warnings:
            result["status"] = "WARNINGS"
        else:
            result["status"] = "PASSED"
        
        return result
    
    def _extract_series_id(self, epr_path: Path) -> str:
        """Extract series ID from EPR filename."""
        name = epr_path.stem
        match = re.search(r'(S\d+)', name)
        return match.group(1) if match else name.replace('_EPR', '')
    
    def _check_documentation(self, content: str) -> Dict[str, Any]:
        """Check for required documentation sections."""
        result = {"status": "UNKNOWN", "issues": [], "warnings": [], "sections_found": []}
        
        required_sections = [
            "Agent Understanding Statement",
            "Book Context",
            "Original Methodology Documentation",
            "Current Methodology Documentation",
            "Original Data Construction",
            "Extension Construction",
            "Transition Analysis",
            "Validation Results",
            "Extension Certification"
        ]
        
        missing = []
        for section in required_sections:
            if section.lower() in content.lower():
                result["sections_found"].append(section)
            else:
                missing.append(section)
        
        if missing:
            result["issues"].append({
                "code": "EXT_MISSING_SECTIONS",
                "message": f"Missing EPR sections: {', '.join(missing)}",
                "severity": "ERROR"
            })
            result["status"] = "INCOMPLETE"
        else:
            result["status"] = "COMPLETE"
        
        result["completeness"] = len(result["sections_found"]) / len(required_sections)
        
        return result
    
    def _check_agent_understanding(self, content: str) -> Dict[str, Any]:
        """Check for agent understanding statement."""
        result = {"status": "UNKNOWN", "issues": [], "warnings": []}
        
        understanding_patterns = [
            r"what is this data\?",
            r"what was the original data source\?",
            r"what methodology was originally applied\?",
            r"what source will be used for extension\?",
            r"have there been methodology updates\?"
        ]
        
        found = sum(1 for p in understanding_patterns if re.search(p, content, re.IGNORECASE))
        
        if found < 3:
            result["issues"].append({
                "code": "EXT_INCOMPLETE_UNDERSTANDING",
                "message": f"Agent understanding statement incomplete ({found}/5 questions addressed)",
                "severity": "ERROR"
            })
            result["status"] = "INCOMPLETE"
        elif found < 5:
            result["warnings"].append({
                "code": "EXT_PARTIAL_UNDERSTANDING",
                "message": f"Agent understanding statement partially complete ({found}/5 questions)",
                "severity": "WARNING"
            })
            result["status"] = "PARTIAL"
        else:
            result["status"] = "COMPLETE"
        
        return result
    
    def _check_book_context(self, content: str) -> Dict[str, Any]:
        """Check for book context with quotes."""
        result = {"status": "UNKNOWN", "issues": [], "warnings": []}
        
        # Check for chapter references
        has_chapter_refs = bool(re.search(r'chapter\s+\d+|ch\s*\d+', content, re.IGNORECASE))
        
        # Check for appendix references
        has_appendix_refs = bool(re.search(r'appendix\s+\d+|app\s*\d+', content, re.IGNORECASE))
        
        # Check for actual quotes (blockquotes)
        quote_count = len(re.findall(r'^>\s*"[^"]+"|^>\s*\[', content, re.MULTILINE))
        
        if not has_chapter_refs and not has_appendix_refs:
            result["issues"].append({
                "code": "EXT_NO_BOOK_CONTEXT",
                "message": "No chapter or appendix references found",
                "severity": "ERROR"
            })
            result["status"] = "MISSING"
        elif quote_count < 2:
            result["warnings"].append({
                "code": "EXT_FEW_QUOTES",
                "message": f"Only {quote_count} quotes found; more quotes recommended",
                "severity": "WARNING"
            })
            result["status"] = "PARTIAL"
        else:
            result["status"] = "COMPLETE"
        
        result["quote_count"] = quote_count
        result["has_chapter_refs"] = has_chapter_refs
        result["has_appendix_refs"] = has_appendix_refs
        
        return result
    
    def _check_methodology(self, content: str) -> Dict[str, Any]:
        """Check methodology documentation and comparison."""
        result = {"status": "UNKNOWN", "issues": [], "warnings": []}
        
        # Check for HDARP references
        has_hdarp_refs = bool(re.search(r'hdarp|knowledge_base', content, re.IGNORECASE))
        
        # Check for methodology comparison
        has_comparison = bool(re.search(r'methodology.*comparison|comparison.*methodology', content, re.IGNORECASE))
        
        # Check for impact assessment
        has_impact = bool(re.search(r'impact\s*:\s*(high|medium|low|none)', content, re.IGNORECASE))
        
        if not has_hdarp_refs:
            result["issues"].append({
                "code": "EXT_NO_HDARP_REFS",
                "message": "No HDARP extraction references found; methodology should reference HDARP files",
                "severity": "ERROR"
            })
        
        if not has_comparison:
            result["warnings"].append({
                "code": "EXT_NO_METHODOLOGY_COMPARISON",
                "message": "Methodology comparison section not clearly identified",
                "severity": "WARNING"
            })
        
        if not has_impact:
            result["warnings"].append({
                "code": "EXT_NO_IMPACT_ASSESSMENT",
                "message": "No impact assessment (HIGH/MEDIUM/LOW/NONE) found",
                "severity": "WARNING"
            })
        
        if not result["issues"] and not result["warnings"]:
            result["status"] = "COMPLETE"
        elif result["issues"]:
            result["status"] = "INCOMPLETE"
        else:
            result["status"] = "PARTIAL"
        
        return result
    
    def _check_transformation(self, content: str) -> Dict[str, Any]:
        """Check transformation chain documentation."""
        result = {"status": "UNKNOWN", "issues": [], "warnings": []}
        
        # Check for transformation IDs
        transform_ids = re.findall(r'T\d{3}', content)
        
        # Check for transformation log reference
        has_log_ref = bool(re.search(r'transformation_log|transform.*log', content, re.IGNORECASE))
        
        # Check for faithful assessment
        has_faithful = bool(re.search(r'faithful\?|faithfulness|faithful:', content, re.IGNORECASE))
        
        if not transform_ids:
            result["issues"].append({
                "code": "EXT_NO_TRANSFORM_IDS",
                "message": "No transformation IDs (T###) found",
                "severity": "ERROR"
            })
        
        if not has_log_ref:
            result["warnings"].append({
                "code": "EXT_NO_LOG_REF",
                "message": "No TRANSFORMATION_LOG reference found",
                "severity": "WARNING"
            })
        
        result["transform_count"] = len(set(transform_ids))
        
        if result["issues"]:
            result["status"] = "INCOMPLETE"
        elif result["warnings"]:
            result["status"] = "PARTIAL"
        else:
            result["status"] = "COMPLETE"
        
        return result
    
    def _check_transition(self, content: str) -> Dict[str, Any]:
        """Check transition analysis documentation."""
        result = {"status": "UNKNOWN", "issues": [], "warnings": [], "metrics": {}}
        
        # Check for transition metrics
        metrics_found = {
            "connection_ratio": bool(re.search(r'connection\s+ratio', content, re.IGNORECASE)),
            "growth_rate": bool(re.search(r'growth\s+rate\s+(continuity|difference)', content, re.IGNORECASE)),
            "trend_alignment": bool(re.search(r'trend\s+alignment|correlation', content, re.IGNORECASE)),
            "level_difference": bool(re.search(r'level\s+difference', content, re.IGNORECASE))
        }
        
        # Check for transition status
        has_status = bool(re.search(r'(seamless|acceptable|problematic|failed)', content, re.IGNORECASE))
        
        # Check for overlap period
        has_overlap = bool(re.search(r'overlap\s+(period|start|end)', content, re.IGNORECASE))
        
        missing_metrics = [k for k, v in metrics_found.items() if not v]
        
        if missing_metrics:
            result["warnings"].append({
                "code": "EXT_MISSING_METRICS",
                "message": f"Missing transition metrics: {', '.join(missing_metrics)}",
                "severity": "WARNING"
            })
        
        if not has_status:
            result["issues"].append({
                "code": "EXT_NO_TRANSITION_STATUS",
                "message": "No transition status (SEAMLESS/ACCEPTABLE/PROBLEMATIC/FAILED) found",
                "severity": "ERROR"
            })
        
        if not has_overlap:
            result["warnings"].append({
                "code": "EXT_NO_OVERLAP_PERIOD",
                "message": "Overlap period not clearly documented",
                "severity": "WARNING"
            })
        
        result["metrics"] = metrics_found
        
        if result["issues"]:
            result["status"] = "INCOMPLETE"
        elif result["warnings"]:
            result["status"] = "PARTIAL"
        else:
            result["status"] = "COMPLETE"
        
        return result
    
    def _check_certification(self, content: str) -> Dict[str, Any]:
        """Check certification section."""
        result = {"status": "UNKNOWN", "issues": [], "warnings": []}
        
        # Check for faithfulness score
        score_match = re.search(r'faithfulness\s+score[:\s]*(\d+)', content, re.IGNORECASE)
        
        # Check for certification status
        cert_status = re.search(r'(certified|certified\s+with\s+notes|not\s+certified)', content, re.IGNORECASE)
        
        # Check for certifying agent
        has_agent = bool(re.search(r'certifying\s+agent|agent.*model', content, re.IGNORECASE))
        
        if not score_match:
            result["issues"].append({
                "code": "EXT_NO_SCORE",
                "message": "No faithfulness score found",
                "severity": "ERROR"
            })
        else:
            result["faithfulness_score"] = int(score_match.group(1))
        
        if not cert_status:
            result["issues"].append({
                "code": "EXT_NO_CERT_STATUS",
                "message": "No certification status found",
                "severity": "ERROR"
            })
        else:
            result["certification_status"] = cert_status.group(1).upper()
        
        if not has_agent:
            result["warnings"].append({
                "code": "EXT_NO_AGENT",
                "message": "No certifying agent documented",
                "severity": "WARNING"
            })
        
        if result["issues"]:
            result["status"] = "INCOMPLETE"
        elif result["warnings"]:
            result["status"] = "PARTIAL"
        else:
            result["status"] = "COMPLETE"
        
        return result
    
    def _calculate_overall_status(self):
        """Calculate overall validation status."""
        if not self.results["series_validated"]:
            self.results["overall_status"] = "NO_EXTENSIONS"
            return
        
        statuses = [s["status"] for s in self.results["series_validated"]]
        
        if all(s == "PASSED" for s in statuses):
            self.results["overall_status"] = "PASSED"
        elif any(s == "FAILED" for s in statuses):
            self.results["overall_status"] = "FAILED"
        elif any(s == "ISSUES" for s in statuses):
            self.results["overall_status"] = "ISSUES"
        else:
            self.results["overall_status"] = "WARNINGS"
        
        # Summary statistics
        self.results["summary"] = {
            "total": len(statuses),
            "passed": statuses.count("PASSED"),
            "warnings": statuses.count("WARNINGS"),
            "issues": statuses.count("ISSUES"),
            "failed": statuses.count("FAILED")
        }


def main():
    parser = argparse.ArgumentParser(
        description="Validate data extensions against Anu Extension Standard v1.0"
    )
    parser.add_argument(
        "project_path",
        help="Path to the project to validate"
    )
    parser.add_argument(
        "--series",
        help="Validate a specific series only"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    # Validate project path
    if not os.path.exists(args.project_path):
        print(f"Error: Project path does not exist: {args.project_path}")
        sys.exit(1)
    
    # Run validation
    validator = ExtensionValidator(args.project_path, verbose=args.verbose)
    
    if args.series:
        results = validator.validate_series(args.series)
    else:
        results = validator.validate_all()
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        _print_report(results)
    
    # Exit code based on status
    if results["overall_status"] == "PASSED":
        sys.exit(0)
    elif results["overall_status"] in ["WARNINGS", "NO_EXTENSIONS"]:
        sys.exit(0)
    else:
        sys.exit(1)


def _print_report(results: Dict[str, Any]):
    """Print human-readable validation report."""
    print("=" * 60)
    print("ANU EXTENSION STANDARD - VALIDATION REPORT")
    print("=" * 60)
    print(f"Version: {results['anu_extension_version']}")
    print(f"Date: {results['validation_date']}")
    print(f"Project: {results['project_path']}")
    print("-" * 60)
    
    if "summary" in results:
        s = results["summary"]
        print(f"\nSUMMARY: {s['total']} extensions validated")
        print(f"  PASSED:   {s['passed']}")
        print(f"  WARNINGS: {s['warnings']}")
        print(f"  ISSUES:   {s['issues']}")
        print(f"  FAILED:   {s['failed']}")
    
    print(f"\nOVERALL STATUS: {results['overall_status']}")
    
    if results["series_validated"]:
        print("\n" + "-" * 60)
        print("SERIES RESULTS:")
        print("-" * 60)
        
        for series in results["series_validated"]:
            status_symbol = {
                "PASSED": "[✓]",
                "WARNINGS": "[!]",
                "ISSUES": "[✗]",
                "FAILED": "[✗✗]"
            }.get(series["status"], "[?]")
            
            print(f"\n{status_symbol} {series['series_id']}: {series['status']}")
            
            if series["issues"]:
                for issue in series["issues"]:
                    print(f"    ERROR: {issue['message']}")
            
            if series["warnings"]:
                for warning in series["warnings"]:
                    print(f"    WARN:  {warning['message']}")
    
    if results["issues"]:
        print("\n" + "-" * 60)
        print("GLOBAL ISSUES:")
        for issue in results["issues"]:
            print(f"  - {issue['message']}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

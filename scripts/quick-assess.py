#!/usr/bin/env python3
"""
Paper Quick Assessment Script
Phase 1.5 自动化速读检查：引用时效性、结构完整性、匿名化、统计指标检测

Usage: python3 quick-assess.py <paper_text_file_or_markdown>

Reads a parsed paper (Markdown/text) and outputs a JSON assessment report.
Can also accept raw text from stdin.
"""

import sys
import json
import re
from collections import Counter
from datetime import datetime


def analyze_references(text: str) -> dict:
    """分析参考文献时效性"""
    current_year = datetime.now().year
    # Match year patterns in references: (2023), 2023, , 2023
    year_pattern = re.compile(r'\b((?:19|20)\d{2})\b')

    # Try to find reference section
    ref_section = ""
    for marker in ["References", "REFERENCES", "Bibliography", "参考文献",
                    "R EFERENCES", "R\nEFERENCES", "REFERENCES\n"]:
        idx = text.rfind(marker)
        if idx != -1:
            ref_section = text[idx:]
            break

    if not ref_section:
        ref_section = text[-8000:]  # fallback: last 8000 chars

    # Extract years - handle both "2023" and ", 2023." patterns
    all_years_raw = year_pattern.findall(ref_section)
    years = [int(y) for y in all_years_raw if 1990 <= int(y) <= current_year + 1]

    # Fallback: search in text around bracketed references [1]...[N]
    if not years:
        # Find regions with [number] patterns (reference entries)
        ref_entries = list(re.finditer(r'\[\d{1,3}\]', text))
        if ref_entries:
            # Use text from first [1] occurrence in last 40% of paper
            tail_start = int(len(text) * 0.6)
            late_refs = [m for m in ref_entries if m.start() >= tail_start]
            if late_refs:
                ref_text = text[late_refs[0].start():]
                all_years_raw = year_pattern.findall(ref_text)
                years = [int(y) for y in all_years_raw if 1990 <= int(y) <= current_year + 1]

    # Final fallback: just search last 40% for any years
    if not years:
        tail = text[int(len(text) * 0.6):]
        all_years_raw = year_pattern.findall(tail)
        years = [int(y) for y in all_years_raw if 1990 <= int(y) <= current_year + 1]

    if not years:
        return {"total_refs": 0, "recent_2yr_ratio": 0, "recent_3yr_ratio": 0, "median_year": 0}

    total = len(years)
    recent_2yr = sum(1 for y in years if y >= current_year - 1)
    recent_3yr = sum(1 for y in years if y >= current_year - 2)
    year_counts = Counter(years)

    return {
        "total_refs": total,
        "recent_2yr_count": recent_2yr,
        "recent_2yr_ratio": round(recent_2yr / total, 2),
        "recent_3yr_count": recent_3yr,
        "recent_3yr_ratio": round(recent_3yr / total, 2),
        "median_year": sorted(years)[len(years) // 2],
        "year_distribution": dict(sorted(year_counts.items())),
        "assessment": "良好" if recent_2yr / total >= 0.25 else "偏旧" if recent_2yr / total >= 0.15 else "严重过时"
    }


def check_structure(text: str) -> dict:
    """检查论文结构完整性"""
    text_lower = text.lower()

    checks = {
        "has_abstract": any(k in text_lower for k in ["abstract", "摘要"]),
        "has_introduction": any(k in text_lower for k in ["introduction", "引言"]),
        "has_related_work": any(k in text_lower for k in ["related work", "related works", "相关工作", "literature review"]),
        "has_method": any(k in text_lower for k in ["method", "approach", "proposed", "methodology", "方法"]),
        "has_experiments": any(k in text_lower for k in ["experiment", "evaluation", "results", "实验"]),
        "has_conclusion": any(k in text_lower for k in ["conclusion", "concluding", "结论"]),
        "has_limitations": any(k in text_lower for k in ["limitation", "limitations", "局限"]),
        "has_broader_impact": any(k in text_lower for k in ["broader impact", "societal impact", "social impact", "ethical"]),
        "has_references": any(k in text_lower for k in ["references", "bibliography", "参考文献"]),
    }

    missing = [k.replace("has_", "").replace("_", " ").title() for k, v in checks.items() if not v]
    score = sum(checks.values()) / len(checks)

    return {
        "checks": checks,
        "missing_sections": missing,
        "completeness_score": round(score, 2),
        "assessment": "完整" if score >= 0.8 else "基本完整" if score >= 0.6 else "结构缺失"
    }


def check_anonymization(text: str) -> dict:
    """检查双盲匿名化合规"""
    issues = []

    # Check for GitHub links
    github_matches = re.findall(r'github\.com/[a-zA-Z0-9_-]+', text)
    if github_matches:
        issues.append(f"发现 GitHub 链接: {', '.join(set(github_matches))}")

    # Check for "our previous work" with specific citations
    if re.search(r'our (previous|prior|earlier) (work|paper|method)', text, re.I):
        issues.append("发现 'our previous work' 表述，可能泄露身份")

    # Check for affiliation mentions in body (not header)
    body = text[500:]  # skip header area
    uni_pattern = re.compile(r'(?:University|Institute|Laboratory|Lab|Inc\.|Corp\.|Google|Microsoft|Meta|Amazon|Apple)\b', re.I)
    uni_matches = uni_pattern.findall(body[:3000])  # check first part of body
    # Only flag if it seems like self-identification, not citations

    # Check for "code will be available"
    if re.search(r'code.{0,20}(available|released|published)', text, re.I):
        issues.append("发现代码公开声明，匿名投稿中可能不合适")

    return {
        "issues": issues,
        "is_anonymous": len(issues) == 0,
        "assessment": "合规" if len(issues) == 0 else f"发现 {len(issues)} 个潜在问题"
    }


def check_statistical_rigor(text: str) -> dict:
    """检测统计严谨性指标"""
    checks = {
        "has_error_bars": bool(re.search(r'±|\\pm|error bar|standard deviation|std\.?dev', text, re.I)),
        "has_multiple_runs": bool(re.search(r'(average|mean).{0,30}(run|trial|seed)|(\d+)\s*(run|trial|seed)', text, re.I)),
        "has_significance_test": bool(re.search(r'(statistical|significance|t-test|p-value|bootstrap|wilcoxon|paired)', text, re.I)),
        "has_confidence_interval": bool(re.search(r'confidence interval|CI\s*[=:]', text, re.I)),
        "has_random_seed": bool(re.search(r'random seed|seed\s*[=:]\s*\d+', text, re.I)),
    }

    score = sum(checks.values()) / len(checks)
    missing = [k.replace("has_", "").replace("_", " ") for k, v in checks.items() if not v]

    return {
        "checks": checks,
        "missing_indicators": missing,
        "rigor_score": round(score, 2),
        "assessment": "严谨" if score >= 0.6 else "基本" if score >= 0.3 else "不足"
    }


def check_efficiency_metrics(text: str) -> dict:
    """检测是否报告了效率指标"""
    checks = {
        "has_params": bool(re.search(r'(param|parameter).{0,20}(count|number|size|\d+[MKB])', text, re.I)),
        "has_flops": bool(re.search(r'(flop|gflop|mflop|mac|gmac)', text, re.I)),
        "has_fps_or_latency": bool(re.search(r'(fps|frame.{0,5}per.{0,5}second|latency|inference.{0,10}time|throughput)', text, re.I)),
        "has_memory": bool(re.search(r'(memory|gpu.{0,10}(usage|consumption)|vram)', text, re.I)),
        "has_training_time": bool(re.search(r'training.{0,15}(time|hour|epoch|day|minute)', text, re.I)),
    }

    reported = [k.replace("has_", "").replace("_", " ") for k, v in checks.items() if v]
    missing = [k.replace("has_", "").replace("_", " ") for k, v in checks.items() if not v]

    return {
        "checks": checks,
        "reported": reported,
        "missing": missing,
        "assessment": "充分" if sum(checks.values()) >= 3 else "部分" if sum(checks.values()) >= 1 else "缺失"
    }


def detect_paper_type(text: str) -> str:
    """识别论文类型"""
    text_lower = text.lower()

    theory_signals = len(re.findall(r'(theorem|lemma|proof|proposition|corollary|convergence|bound)', text_lower))
    experiment_signals = len(re.findall(r'(dataset|benchmark|baseline|ablation|comparison|evaluation)', text_lower))
    application_signals = len(re.findall(r'(deploy|real-world|production|industrial|clinical|practical)', text_lower))
    survey_signals = len(re.findall(r'(survey|review|taxonomy|categoriz|overview of)', text_lower))

    scores = {
        "理论型": theory_signals,
        "实验型": experiment_signals,
        "应用型": application_signals,
        "综述型": survey_signals,
    }

    primary = max(scores, key=scores.get)
    if scores["理论型"] > 5 and scores["实验型"] > 5:
        return "理论+实验型"
    return primary


def main():
    if len(sys.argv) < 2:
        text = sys.stdin.read()
    else:
        with open(sys.argv[1], "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    if not text.strip():
        print(json.dumps({"error": "Empty input"}, ensure_ascii=False))
        sys.exit(1)

    report = {
        "paper_type": detect_paper_type(text),
        "reference_timeliness": analyze_references(text),
        "structure_completeness": check_structure(text),
        "anonymization": check_anonymization(text),
        "statistical_rigor": check_statistical_rigor(text),
        "efficiency_metrics": check_efficiency_metrics(text),
    }

    # Overall quick assessment
    signals = []
    if report["reference_timeliness"]["recent_2yr_ratio"] >= 0.25:
        signals.append("✅ 引用时效性良好")
    else:
        signals.append("⚠️ 引用偏旧")

    if report["structure_completeness"]["completeness_score"] >= 0.8:
        signals.append("✅ 结构完整")
    else:
        signals.append(f"⚠️ 缺少: {', '.join(report['structure_completeness']['missing_sections'])}")

    if report["anonymization"]["is_anonymous"]:
        signals.append("✅ 匿名化合规")
    else:
        signals.append(f"⚠️ 匿名化问题: {'; '.join(report['anonymization']['issues'])}")

    if report["statistical_rigor"]["rigor_score"] >= 0.3:
        signals.append("✅ 有统计指标")
    else:
        signals.append("⚠️ 缺少统计严谨性指标 (无 error bars / 多次运行)")

    if report["efficiency_metrics"]["assessment"] != "缺失":
        signals.append(f"✅ 有效率指标: {', '.join(report['efficiency_metrics']['reported'])}")
    else:
        signals.append("⚠️ 未报告效率指标 (Params/FLOPs/FPS)")

    report["quick_signals"] = signals
    report["overall_impression"] = "正面" if signals.count("✅") >= 4 else "中性" if signals.count("✅") >= 2 else "需关注"

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

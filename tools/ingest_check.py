#!/usr/bin/env python3
"""
GAP Ingest Check

Runs the same QAT and anti-sybil checks locally that the ingest service performs.
Provides transparency and lets partners verify their shards before upload.
"""

import click
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "gap-agent" / "src"))

try:
    from gap_agent.dedupe import precheck_shard, detect_video_duplicates, detect_control_duplicates
    from validate import GAPValidator
    HAVE_DEPS = True
except ImportError:
    HAVE_DEPS = False


def run_qat_checks(shard_path: str, profile: Optional[str] = None) -> Dict[str, Any]:
    """Run Quality Acceptance Tests on GAP shard."""
    
    if not HAVE_DEPS:
        return {"error": "Dependencies not available for QAT checks"}
    
    try:
        validator = GAPValidator(shard_path, profile, strict=False)
        is_valid, report = validator.validate_all()
        
        return {
            "qat_passed": is_valid,
            "qat_report": report
        }
    except Exception as e:
        return {"error": f"QAT check failed: {e}"}


def run_anti_sybil_checks(shard_path: str, cache_path: Optional[str] = None) -> Dict[str, Any]:
    """Run anti-sybil duplicate detection checks."""
    
    if not HAVE_DEPS:
        return {"error": "Dependencies not available for anti-sybil checks"}
    
    try:
        # Run precheck (includes both video and controls duplicate detection)
        precheck_result = precheck_shard(shard_path, cache_path)
        
        # Calculate risk score similar to server-side
        video_check = precheck_result.get('video_check', {})
        controls_check = precheck_result.get('controls_check', {})
        
        risk_score = 0
        
        # Video similarity scoring (0-40 points)
        video_min_dist = video_check.get('min_distance', 128)
        if video_min_dist <= 8:
            risk_score += 40
        elif video_min_dist <= 16:
            risk_score += 20
        
        # Control similarity scoring (0-30 points)
        controls_min_dist = controls_check.get('min_distance', 64)
        if controls_min_dist <= 8:
            risk_score += 30
        elif controls_min_dist <= 16:
            risk_score += 15
        
        # Overall risk assessment
        if risk_score >= 80:
            action = "reject"
            risk_level = "high"
        elif risk_score >= 50:
            action = "flag"
            risk_level = "high"
        elif risk_score >= 30:
            action = "review"
            risk_level = "medium"
        else:
            action = "accept"
            risk_level = "low"
        
        return {
            "anti_sybil_passed": action == "accept",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "action": action,
            "video_check": video_check,
            "controls_check": controls_check,
            "precheck_result": precheck_result
        }
        
    except Exception as e:
        return {"error": f"Anti-sybil check failed: {e}"}


def estimate_server_acceptance(qat_result: Dict[str, Any], 
                             antisybil_result: Dict[str, Any]) -> Dict[str, Any]:
    """Estimate likelihood of server acceptance based on local checks."""
    
    qat_passed = qat_result.get('qat_passed', False)
    antisybil_passed = antisybil_result.get('anti_sybil_passed', False)
    risk_score = antisybil_result.get('risk_score', 100)
    
    # Base acceptance probability
    if qat_passed and antisybil_passed:
        base_prob = 0.95
    elif qat_passed and not antisybil_passed:
        base_prob = 0.3  # QAT passed but duplicate risk
    elif not qat_passed and antisybil_passed:
        base_prob = 0.2  # No duplicates but QAT failed
    else:
        base_prob = 0.05  # Both failed
    
    # Adjust for risk score
    risk_penalty = min(risk_score / 100, 0.8)  # Max 80% penalty
    final_prob = base_prob * (1 - risk_penalty)
    
    # Determine outcome
    if final_prob >= 0.8:
        outcome = "likely_accept"
        recommendation = "✅ Upload recommended - high acceptance probability"
    elif final_prob >= 0.5:
        outcome = "moderate_accept"
        recommendation = "⚠️ Upload possible - moderate acceptance probability"
    elif final_prob >= 0.2:
        outcome = "unlikely_accept"
        recommendation = "🔶 Upload risky - low acceptance probability"
    else:
        outcome = "reject"
        recommendation = "❌ Upload not recommended - very low acceptance probability"
    
    return {
        "estimated_acceptance_probability": final_prob,
        "outcome": outcome,
        "recommendation": recommendation
    }


@click.command()
@click.argument('shard_path', type=click.Path(exists=True))
@click.option('--profile', help='GAP profile for validation')
@click.option('--cache', help='Path to duplicate detection cache')
@click.option('--json', 'output_json', is_flag=True, help='JSON output')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(shard_path: str, profile: Optional[str], cache: Optional[str], 
         output_json: bool, verbose: bool):
    """
    Run ingest checks on GAP shard.
    
    Performs the same QAT and anti-sybil checks that the server ingest pipeline runs.
    Helps partners verify their shards locally before upload.
    """
    
    if not HAVE_DEPS:
        click.echo("❌ Missing dependencies. Please install gap-agent package.", err=True)
        sys.exit(1)
    
    click.echo(f"🔍 Running ingest checks on: {shard_path}")
    if profile:
        click.echo(f"   Profile: {profile}")
    if cache:
        click.echo(f"   Cache: {cache}")
    
    # Run QAT checks
    click.echo("\n📋 Running Quality Acceptance Tests...")
    qat_result = run_qat_checks(shard_path, profile)
    
    if verbose and not output_json:
        if qat_result.get('qat_passed'):
            click.echo("   ✅ QAT checks passed")
        else:
            click.echo("   ❌ QAT checks failed")
            
        # Show QAT details
        qat_report = qat_result.get('qat_report', {})
        if qat_report.get('errors'):
            click.echo("   Errors:")
            for error in qat_report['errors']:
                click.echo(f"     - {error}")
        if qat_report.get('warnings'):
            click.echo("   Warnings:")
            for warning in qat_report['warnings']:
                click.echo(f"     - {warning}")
    
    # Run anti-sybil checks
    click.echo("\n🛡️  Running anti-sybil checks...")
    antisybil_result = run_anti_sybil_checks(shard_path, cache)
    
    if verbose and not output_json:
        if antisybil_result.get('anti_sybil_passed'):
            click.echo("   ✅ Anti-sybil checks passed")
        else:
            click.echo("   ❌ Anti-sybil checks flagged content")
            
        risk_score = antisybil_result.get('risk_score', 0)
        risk_level = antisybil_result.get('risk_level', 'unknown')
        click.echo(f"   Risk Score: {risk_score}/100 ({risk_level})")
        
        action = antisybil_result.get('action', 'unknown')
        click.echo(f"   Recommended Action: {action}")
    
    # Estimate server acceptance
    click.echo("\n🎯 Estimating server acceptance...")
    acceptance_estimate = estimate_server_acceptance(qat_result, antisybil_result)
    
    if not output_json:
        click.echo(f"   {acceptance_estimate['recommendation']}")
        click.echo(f"   Estimated Probability: {acceptance_estimate['estimated_acceptance_probability']:.1%}")
    
    # Generate final report
    final_report = {
        "shard_path": shard_path,
        "profile": profile,
        "timestamp": click.utils.format_filename(str(Path(shard_path).stat().st_mtime)),
        "qat_checks": qat_result,
        "anti_sybil_checks": antisybil_result,
        "server_acceptance_estimate": acceptance_estimate
    }
    
    if output_json:
        click.echo(json.dumps(final_report, indent=2))
    else:
        click.echo(f"\n📊 Summary:")
        click.echo(f"   QAT: {'✅ PASS' if qat_result.get('qat_passed') else '❌ FAIL'}")
        click.echo(f"   Anti-sybil: {'✅ PASS' if antisybil_result.get('anti_sybil_passed') else '❌ FAIL'}")
        click.echo(f"   Overall: {acceptance_estimate['recommendation']}")
        
        if not qat_result.get('qat_passed') or not antisybil_result.get('anti_sybil_passed'):
            click.echo(f"\n💡 Use --verbose for detailed error information")
    
    # Exit code based on overall result
    if acceptance_estimate['outcome'] in ['likely_accept', 'moderate_accept']:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main() 
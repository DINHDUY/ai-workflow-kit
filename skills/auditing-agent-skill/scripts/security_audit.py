#!/usr/bin/env python3
"""
Security Audit Tool for AI Agent Skills
Checks for prompt injection, unsafe code execution, and other vulnerabilities
"""

import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class SecurityFinding:
    """Represents a security vulnerability finding"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str
    description: str
    line_number: int
    code_snippet: str
    recommendation: str
    cwe_id: str  # Common Weakness Enumeration ID

class SkillSecurityAuditor:
    """Comprehensive security auditor for AI Agent Skills"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.findings: List[SecurityFinding] = []
        
    def audit_skill(self, skill_path: Path) -> Dict[str, Any]:
        """Run comprehensive security audit on a skill"""
        content = skill_path.read_text()
        lines = content.split('\n')
        
        # Run all security checks
        self.check_prompt_injection(lines)
        self.check_unsafe_code_execution(lines)
        self.check_file_system_access(lines)
        self.check_credential_exposure(lines)
        self.check_input_validation(lines)
        self.check_command_injection(lines)
        self.check_network_security(lines)
        self.check_data_sanitization(lines)
        
        return self.generate_report(skill_path)
    
    def check_prompt_injection(self, lines: List[str]):
        """Detect prompt injection vulnerabilities"""
        
        # Pattern 1: Unvalidated user input in prompts
        injection_patterns = [
            (r'user[_\s]+input.*(?:prompt|query|message)',
             'User input directly concatenated into prompts without sanitization',
             'CWE-74'),
            (r'\$\{.*user.*\}', 
             'Template interpolation with user data',
             'CWE-74'),
            (r'f["\'].*\{.*user.*\}', 
             'F-string with unsanitized user input',
             'CWE-74'),
            (r'eval\s*\(.*user',
             'Eval with user-controlled input - CRITICAL',
             'CWE-95'),
        ]
        
        # Pattern 2: Missing input boundaries
        boundary_patterns = [
            (r'(?<!sanitize).*(?:input|query|message).*(?:\+|concat)',
             'String concatenation without boundary markers',
             'CWE-74'),
        ]
        
        # Pattern 3: Instruction override risks
        override_patterns = [
            (r'(?:system|instruction|rule).*(?:ignore|disregard|forget)',
             'Potential instruction override keywords detected',
             'CWE-74'),
            (r'(?:previous|above|prior).*(?:instruction|command|directive)',
             'Reference to override previous instructions',
             'CWE-74'),
        ]
        
        for i, line in enumerate(lines, 1):
            # Check all patterns
            for pattern, desc, cwe in injection_patterns + boundary_patterns + override_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    severity = 'CRITICAL' if 'eval' in pattern else 'HIGH'
                    self.findings.append(SecurityFinding(
                        severity=severity,
                        category='PROMPT_INJECTION',
                        description=desc,
                        line_number=i,
                        code_snippet=line.strip()[:100],
                        recommendation='Use input sanitization, boundary markers (XML tags, delimiters), and validate against injection patterns. Never concatenate raw user input into prompts.',
                        cwe_id=cwe
                    ))
    
    def check_unsafe_code_execution(self, lines: List[str]):
        """Detect unsafe code execution patterns"""
        
        dangerous_patterns = [
            (r'\bexec\s*\(', 'CRITICAL', 
             'exec() allows arbitrary code execution', 
             'Never use exec(). Use safe alternatives like ast.literal_eval() for data.',
             'CWE-95'),
            (r'\beval\s*\(', 'CRITICAL',
             'eval() allows arbitrary code execution',
             'Replace eval() with ast.literal_eval() or json.loads() for safe parsing.',
             'CWE-95'),
            (r'__import__\s*\(.*user', 'CRITICAL',
             'Dynamic import with user-controlled input',
             'Use static imports or whitelist allowed modules.',
             'CWE-94'),
            (r'compile\s*\(.*user', 'HIGH',
             'Code compilation with user input',
             'Avoid dynamic compilation. Use predefined, validated code paths.',
             'CWE-94'),
            (r'os\.system\s*\(', 'HIGH',
             'os.system() allows shell injection',
             'Use subprocess.run() with shell=False and argument list.',
             'CWE-78'),
            (r'subprocess.*shell\s*=\s*True', 'HIGH',
             'Shell=True enables command injection',
             'Set shell=False and pass arguments as list.',
             'CWE-78'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, severity, desc, rec, cwe in dangerous_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.findings.append(SecurityFinding(
                        severity=severity,
                        category='UNSAFE_CODE_EXECUTION',
                        description=desc,
                        line_number=i,
                        code_snippet=line.strip()[:100],
                        recommendation=rec,
                        cwe_id=cwe
                    ))
    
    def check_file_system_access(self, lines: List[str]):
        """Detect file system security issues"""
        
        fs_patterns = [
            (r'open\s*\(.*user.*["\']w["\']', 'HIGH',
             'Writing to user-controlled file path',
             'Validate and sanitize file paths. Use Path().resolve() and check against allowed directories.',
             'CWE-22'),
            (r'os\.path\.join\s*\(.*user', 'MEDIUM',
             'Path traversal risk with user input',
             'Validate path components. Check for ".." and absolute paths. Use Path().resolve() and verify result is within allowed directory.',
             'CWE-22'),
            (r'\.\.[\\/]', 'HIGH',
             'Path traversal pattern detected',
             'Reject paths containing ".." or validate that resolved path is within allowed scope.',
             'CWE-22'),
            (r'os\.remove\s*\(.*user', 'HIGH',
             'File deletion with user-controlled path',
             'Strictly validate paths before deletion. Never allow user to specify arbitrary deletion targets.',
             'CWE-22'),
            (r'/etc/|/root/|C:\\\\Windows', 'CRITICAL',
             'Access to system directories',
             'Restrict file operations to application-specific directories only.',
             'CWE-22'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, severity, desc, rec, cwe in fs_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.findings.append(SecurityFinding(
                        severity=severity,
                        category='FILE_SYSTEM_ACCESS',
                        description=desc,
                        line_number=i,
                        code_snippet=line.strip()[:100],
                        recommendation=rec,
                        cwe_id=cwe
                    ))
    
    def check_credential_exposure(self, lines: List[str]):
        """Detect credential and secret exposure risks"""
        
        credential_patterns = [
            (r'(?:api[_-]?key|apikey)\s*=\s*["\'][^"\']+["\']', 'CRITICAL',
             'Hardcoded API key detected',
             'Use environment variables or secret management system. Never commit credentials.',
             'CWE-798'),
            (r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']+["\']', 'CRITICAL',
             'Hardcoded password detected',
             'Use environment variables or secure credential storage.',
             'CWE-798'),
            (r'(?:secret|token)\s*=\s*["\'][^"\']{20,}["\']', 'CRITICAL',
             'Hardcoded secret/token detected',
             'Use environment variables (os.environ.get()) or secret management.',
             'CWE-798'),
            (r'Bearer\s+[A-Za-z0-9_-]{20,}', 'HIGH',
             'Bearer token in code',
             'Load tokens from secure storage, not source code.',
             'CWE-798'),
            (r'(?:aws_access_key|AWS_ACCESS_KEY)', 'CRITICAL',
             'AWS credentials in code',
             'Use IAM roles or AWS credential profiles.',
             'CWE-798'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, severity, desc, rec, cwe in credential_patterns:
                if re.search(pattern, line):
                    self.findings.append(SecurityFinding(
                        severity=severity,
                        category='CREDENTIAL_EXPOSURE',
                        description=desc,
                        line_number=i,
                        code_snippet='[REDACTED - credential detected]',
                        recommendation=rec,
                        cwe_id=cwe
                    ))
    
    def check_input_validation(self, lines: List[str]):
        """Detect missing input validation"""
        
        validation_patterns = [
            (r'request\.(?:args|form|json)\[.*\](?!.*(?:validate|sanitize|clean))', 'MEDIUM',
             'User input used without validation',
             'Validate all user input against expected format/type/range.',
             'CWE-20'),
            (r'input\s*\(.*\)(?!.*(?:validate|sanitize|int|float))', 'MEDIUM',
             'User input without type validation',
             'Validate and convert input to expected type with error handling.',
             'CWE-20'),
            (r'sql.*\+.*user|sql.*f["\'].*\{user', 'CRITICAL',
             'SQL injection vulnerability',
             'Use parameterized queries or ORM. Never concatenate user input into SQL.',
             'CWE-89'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, severity, desc, rec, cwe in validation_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.findings.append(SecurityFinding(
                        severity=severity,
                        category='INPUT_VALIDATION',
                        description=desc,
                        line_number=i,
                        code_snippet=line.strip()[:100],
                        recommendation=rec,
                        cwe_id=cwe
                    ))
    
    def check_command_injection(self, lines: List[str]):
        """Detect command injection vulnerabilities"""
        
        cmd_patterns = [
            (r'(?:os\.system|subprocess\.call|subprocess\.run)\s*\(.*(?:\+|f["\']|%|\.format)', 'CRITICAL',
             'Command injection via string concatenation',
             'Pass commands as list, not string. Use shell=False. Validate all arguments.',
             'CWE-78'),
            (r'bash.*-c.*user|sh.*-c.*user', 'CRITICAL',
             'Shell command with user input',
             'Never pass user input to shell. Use specific commands with validated arguments.',
             'CWE-78'),
            (r'Popen\s*\(.*shell\s*=\s*True', 'HIGH',
             'Popen with shell=True enables injection',
             'Use shell=False and pass command as list.',
             'CWE-78'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, severity, desc, rec, cwe in cmd_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.findings.append(SecurityFinding(
                        severity=severity,
                        category='COMMAND_INJECTION',
                        description=desc,
                        line_number=i,
                        code_snippet=line.strip()[:100],
                        recommendation=rec,
                        cwe_id=cwe
                    ))
    
    def check_network_security(self, lines: List[str]):
        """Detect network security issues"""
        
        network_patterns = [
            (r'verify\s*=\s*False', 'HIGH',
             'SSL verification disabled',
             'Enable SSL verification. Use valid certificates.',
             'CWE-295'),
            (r'http://(?!localhost|127\.0\.0\.1)', 'MEDIUM',
             'Unencrypted HTTP connection',
             'Use HTTPS for all external connections.',
             'CWE-319'),
            (r'requests\.get\s*\(.*user.*\)(?!.*timeout)', 'MEDIUM',
             'HTTP request without timeout',
             'Set timeout parameter to prevent hanging.',
             'CWE-400'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, severity, desc, rec, cwe in network_patterns:
                if re.search(pattern, line):
                    self.findings.append(SecurityFinding(
                        severity=severity,
                        category='NETWORK_SECURITY',
                        description=desc,
                        line_number=i,
                        code_snippet=line.strip()[:100],
                        recommendation=rec,
                        cwe_id=cwe
                    ))
    
    def check_data_sanitization(self, lines: List[str]):
        """Detect data sanitization issues"""
        
        sanitization_patterns = [
            (r'print\s*\(.*(?:password|secret|token|key)', 'HIGH',
             'Sensitive data in print statement',
             'Never log sensitive data. Use redaction for debugging.',
             'CWE-532'),
            (r'log.*(?:password|secret|token|key)', 'HIGH',
             'Sensitive data in logs',
             'Redact sensitive fields before logging.',
             'CWE-532'),
            (r'json\.dumps\s*\(.*(?:password|secret)', 'MEDIUM',
             'Sensitive data in JSON output',
             'Exclude sensitive fields from serialization.',
             'CWE-532'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, severity, desc, rec, cwe in sanitization_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.findings.append(SecurityFinding(
                        severity=severity,
                        category='DATA_SANITIZATION',
                        description=desc,
                        line_number=i,
                        code_snippet=line.strip()[:100],
                        recommendation=rec,
                        cwe_id=cwe
                    ))
    
    def generate_report(self, skill_path: Path) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        
        # Sort findings by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_findings = sorted(
            self.findings, 
            key=lambda x: (severity_order[x.severity], x.line_number)
        )
        
        # Calculate statistics
        stats = {
            'total_findings': len(sorted_findings),
            'critical': sum(1 for f in sorted_findings if f.severity == 'CRITICAL'),
            'high': sum(1 for f in sorted_findings if f.severity == 'HIGH'),
            'medium': sum(1 for f in sorted_findings if f.severity == 'MEDIUM'),
            'low': sum(1 for f in sorted_findings if f.severity == 'LOW'),
            'categories': {}
        }
        
        for finding in sorted_findings:
            stats['categories'][finding.category] = \
                stats['categories'].get(finding.category, 0) + 1
        
        # Determine overall security posture
        if stats['critical'] > 0:
            posture = 'UNSAFE - Critical vulnerabilities must be fixed'
        elif stats['high'] > 3:
            posture = 'RISKY - Multiple high-severity issues found'
        elif stats['high'] > 0:
            posture = 'NEEDS_IMPROVEMENT - High-severity issues should be addressed'
        elif stats['medium'] > 5:
            posture = 'MODERATE - Consider addressing medium-severity findings'
        elif stats['medium'] > 0:
            posture = 'ACCEPTABLE - Minor improvements recommended'
        else:
            posture = 'SECURE - No significant vulnerabilities detected'
        
        return {
            'skill_path': str(skill_path),
            'audit_timestamp': '2026-02-13',
            'security_posture': posture,
            'statistics': stats,
            'findings': [asdict(f) for f in sorted_findings]
        }
    
    def print_report(self, report: Dict[str, Any]):
        """Print human-readable security report"""
        
        print("\n" + "="*80)
        print(f"SECURITY AUDIT REPORT: {report['skill_path']}")
        print("="*80 + "\n")
        
        print(f"Security Posture: {report['security_posture']}\n")
        
        stats = report['statistics']
        print(f"Total Findings: {stats['total_findings']}")
        print(f"  ├─ CRITICAL: {stats['critical']}")
        print(f"  ├─ HIGH:     {stats['high']}")
        print(f"  ├─ MEDIUM:   {stats['medium']}")
        print(f"  └─ LOW:      {stats['low']}\n")
        
        if stats['categories']:
            print("Findings by Category:")
            for category, count in sorted(stats['categories'].items(), 
                                         key=lambda x: x[1], reverse=True):
                print(f"  • {category}: {count}")
            print()
        
        if report['findings']:
            print("\nDETAILED FINDINGS:")
            print("-"*80 + "\n")
            
            for i, finding in enumerate(report['findings'], 1):
                severity_color = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🔵'
                }
                
                print(f"{i}. {severity_color.get(finding['severity'], '⚪')} "
                      f"[{finding['severity']}] {finding['category']}")
                print(f"   Line {finding['line_number']}: {finding['description']}")
                print(f"   Code: {finding['code_snippet']}")
                print(f"   CWE:  {finding['cwe_id']}")
                print(f"   Fix:  {finding['recommendation']}\n")
        else:
            print("✅ No security vulnerabilities detected!\n")
        
        print("="*80)
        print("Audit complete. Review all findings before deploying this skill.")
        print("="*80 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description='Security audit tool for AI Agent Skills'
    )
    parser.add_argument('skill_path', type=Path,
                       help='Path to SKILL.md file to audit')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('-o', '--output', type=Path,
                       help='Write JSON report to file')
    parser.add_argument('--fix-suggestions', action='store_true',
                       help='Include detailed fix suggestions')
    
    args = parser.parse_args()
    
    if not args.skill_path.exists():
        print(f"Error: Skill file not found: {args.skill_path}")
        return 1
    
    # Run audit
    auditor = SkillSecurityAuditor(verbose=args.verbose)
    report = auditor.audit_skill(args.skill_path)
    
    # Print to console
    auditor.print_report(report)
    
    # Save JSON report if requested
    if args.output:
        args.output.write_text(json.dumps(report, indent=2))
        print(f"\n📄 Full report saved to: {args.output}")
    
    # Return non-zero if critical/high severity issues found
    stats = report['statistics']
    return 0 if (stats['critical'] + stats['high']) == 0 else 1

if __name__ == '__main__':
    exit(main())

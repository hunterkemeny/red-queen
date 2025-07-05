#!/usr/bin/env python3
"""
Beautiful CLI interface for Red Queen benchmarking suite.
"""

import sys
import os
from typing import Optional, List, Dict, Any


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    PURPLE = '\033[35m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'


class BeautifulCLI:
    """Beautiful command-line interface for Red Queen."""
    
    def __init__(self):
        try:
            self.terminal_width = min(os.get_terminal_size().columns, 120)
        except OSError:
            # Handle case where stdout is redirected or not a terminal
            self.terminal_width = 80
        self.config = {}
        
    def print_welcome(self):
        """Print beautiful welcome screen."""
        print(f"\n{Colors.HEADER}{'='*self.terminal_width}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}🚀 RED QUEEN QUANTUM BENCHMARKING SUITE 🚀{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*self.terminal_width}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}Welcome to Red Queen!{Colors.ENDC}")
        print(f"{Colors.GRAY}A comprehensive quantum compiler benchmarking framework{Colors.ENDC}")
        print(f"{Colors.HEADER}{'-'*self.terminal_width}{Colors.ENDC}")
        
    def get_compiler_choice(self) -> str:
        """Get compiler choice with beautiful interface."""
        print(f"\n{Colors.BOLD}📋 Step 1: Choose Primary Compiler{Colors.ENDC}")
        print(f"{Colors.GRAY}Select the quantum compiler you want to benchmark{Colors.ENDC}\n")
        
        compilers = {
            '1': {'name': 'qiskit', 'desc': 'IBM Qiskit - Industry standard quantum computing framework'},
            '2': {'name': 'pytket', 'desc': 'Cambridge Quantum Computing TKET - High-performance compiler'}
        }
        
        for key, info in compilers.items():
            print(f"  {Colors.OKBLUE}[{key}]{Colors.ENDC} {Colors.BOLD}{info['name']}{Colors.ENDC}")
            print(f"      {Colors.GRAY}{info['desc']}{Colors.ENDC}")
            
        while True:
            choice = input(f"\n{Colors.BOLD}➤ Enter your choice (1-2): {Colors.ENDC}").strip()
            
            if choice in compilers:
                compiler = compilers[choice]['name']
                print(f"  {Colors.OKGREEN}✓ Selected: {compiler}{Colors.ENDC}")
                return compiler
            else:
                print(f"  {Colors.FAIL}✗ Invalid choice. Please enter 1 or 2.{Colors.ENDC}")
                
    def get_version(self, compiler: str) -> str:
        """Get compiler version with suggestions."""
        print(f"\n{Colors.BOLD}📦 Step 2: Specify {compiler.title()} Version{Colors.ENDC}")
        
        # Try to get latest versions dynamically
        try:
            import subprocess
            result = subprocess.run(
                ['python3', 'get_versions.py', compiler],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                suggestions = result.stdout.strip().split('\n')[:3]
            else:
                raise Exception("Failed to get versions")
        except:
            # Fallback to static suggestions
            fallback_suggestions = {
                'qiskit': ['1.0', '0.45.0', '0.44.0'],
                'pytket': ['2.7.0', '2.6.0', '2.5.0']
            }
            suggestions = fallback_suggestions.get(compiler, ['latest'])
        
        if suggestions and suggestions[0]:
            print(f"{Colors.GRAY}Popular versions:{Colors.ENDC}")
            for i, version in enumerate(suggestions, 1):
                print(f"  {Colors.OKBLUE}[{i}]{Colors.ENDC} {version}")
                
        while True:
            version = input(f"\n{Colors.BOLD}➤ Enter version (or number from above): {Colors.ENDC}").strip()
            
            # Check if it's a number selection
            if version.isdigit() and int(version) <= len(suggestions):
                version = suggestions[int(version) - 1]
                
            if version:
                print(f"  {Colors.OKGREEN}✓ Version: {version}{Colors.ENDC}")
                return version
            else:
                print(f"  {Colors.FAIL}✗ Please enter a valid version.{Colors.ENDC}")
                
    def get_optimization_level(self, compiler: str) -> int:
        """Get optimization level with explanations."""
        print(f"\n{Colors.BOLD}⚡ Step 3: Choose Optimization Level{Colors.ENDC}")
        print(f"{Colors.GRAY}Higher levels provide better optimization but take longer{Colors.ENDC}\n")
        
        levels = {
            'qiskit': {
                '0': 'No optimization - fastest compilation',
                '1': 'Light optimization - good balance',
                '2': 'Medium optimization - better circuits',
                '3': 'Heavy optimization - best circuits, slowest'
            },
            'pytket': {
                '0': 'No optimization - fastest compilation',
                '1': 'Light optimization - good balance', 
                '2': 'Medium optimization - better circuits'
            }
        }
        
        available_levels = levels.get(compiler, levels['qiskit'])
        
        for level, desc in available_levels.items():
            print(f"  {Colors.OKBLUE}[{level}]{Colors.ENDC} {Colors.BOLD}Level {level}{Colors.ENDC} - {Colors.GRAY}{desc}{Colors.ENDC}")
            
        while True:
            level = input(f"\n{Colors.BOLD}➤ Enter optimization level: {Colors.ENDC}").strip()
            
            if level in available_levels:
                print(f"  {Colors.OKGREEN}✓ Optimization Level: {level}{Colors.ENDC}")
                return int(level)
            else:
                max_level = max(available_levels.keys())
                print(f"  {Colors.FAIL}✗ Invalid level. Please enter 0-{max_level}.{Colors.ENDC}")
                
    def get_second_compiler(self) -> Optional[Dict[str, Any]]:
        """Get optional second compiler for comparison."""
        print(f"\n{Colors.BOLD}🔄 Step 4: Optional Second Compiler{Colors.ENDC}")
        print(f"{Colors.GRAY}Compare performance against another compiler (optional){Colors.ENDC}\n")
        
        print(f"  {Colors.OKBLUE}[1]{Colors.ENDC} {Colors.BOLD}Yes{Colors.ENDC} - Add second compiler for comparison")
        print(f"  {Colors.OKBLUE}[2]{Colors.ENDC} {Colors.BOLD}No{Colors.ENDC} - Benchmark single compiler only")
        
        while True:
            choice = input(f"\n{Colors.BOLD}➤ Add second compiler? (1-2): {Colors.ENDC}").strip()
            
            if choice == '2' or choice.lower() in ['n', 'no']:
                print(f"  {Colors.OKGREEN}✓ Single compiler benchmarking{Colors.ENDC}")
                return None
            elif choice == '1' or choice.lower() in ['y', 'yes']:
                print(f"  {Colors.OKGREEN}✓ Adding second compiler{Colors.ENDC}")
                
                # Get second compiler (different from first)
                compiler2 = self.get_compiler_choice()
                version2 = self.get_version(compiler2)
                opt_level2 = self.get_optimization_level(compiler2)
                
                return {
                    'compiler': compiler2,
                    'version': version2,
                    'optimization_level': opt_level2
                }
            else:
                print(f"  {Colors.FAIL}✗ Please enter 1 or 2.{Colors.ENDC}")
                
    def get_backend(self) -> str:
        """Get backend choice with explanations."""
        print(f"\n{Colors.BOLD}🖥️  Step 5: Choose Backend{Colors.ENDC}")
        print(f"{Colors.GRAY}Select the quantum hardware backend to simulate{Colors.ENDC}\n")
        
        backends = {
            '1': {'name': 'FakeWashingtonV2', 'desc': 'IBM Washington - 127 qubits, heavy-hex topology'},
            '2': {'name': 'FakeManhattanV2', 'desc': 'IBM Manhattan - 65 qubits, heavy-hex topology'},
            '3': {'name': 'FakeTorontoV2', 'desc': 'IBM Toronto - 27 qubits, heavy-hex topology'},
            '4': {'name': 'FakeAthensV2', 'desc': 'IBM Athens - 5 qubits, linear topology'},
            '5': {'name': 'custom', 'desc': 'Enter custom backend name'}
        }
        
        for key, info in backends.items():
            print(f"  {Colors.OKBLUE}[{key}]{Colors.ENDC} {Colors.BOLD}{info['name']}{Colors.ENDC}")
            print(f"      {Colors.GRAY}{info['desc']}{Colors.ENDC}")
            
        print(f"\n  {Colors.YELLOW}💡 Tip: Press Enter for default (FakeWashingtonV2){Colors.ENDC}")
        
        while True:
            choice = input(f"\n{Colors.BOLD}➤ Enter your choice (1-5 or Enter for default): {Colors.ENDC}").strip()
            
            if not choice:  # Default
                backend = 'FakeWashingtonV2'
                print(f"  {Colors.OKGREEN}✓ Using default: {backend}{Colors.ENDC}")
                return backend
            elif choice in backends:
                if choice == '5':  # Custom
                    backend = input(f"  {Colors.BOLD}➤ Enter custom backend name: {Colors.ENDC}").strip()
                    if backend:
                        print(f"  {Colors.OKGREEN}✓ Custom backend: {backend}{Colors.ENDC}")
                        return backend
                    else:
                        print(f"  {Colors.FAIL}✗ Please enter a valid backend name.{Colors.ENDC}")
                        continue
                else:
                    backend = backends[choice]['name']
                    print(f"  {Colors.OKGREEN}✓ Selected: {backend}{Colors.ENDC}")
                    return backend
            else:
                print(f"  {Colors.FAIL}✗ Invalid choice. Please enter 1-5 or press Enter.{Colors.ENDC}")
                
    def get_num_runs(self) -> int:
        """Get number of runs for statistics."""
        print(f"\n{Colors.BOLD}🔢 Step 6: Number of Runs{Colors.ENDC}")
        print(f"{Colors.GRAY}More runs provide better statistical accuracy{Colors.ENDC}\n")
        
        print(f"  {Colors.OKBLUE}[1]{Colors.ENDC} {Colors.BOLD}1 run{Colors.ENDC} - Quick test")
        print(f"  {Colors.OKBLUE}[2]{Colors.ENDC} {Colors.BOLD}3 runs{Colors.ENDC} - Basic statistics")
        print(f"  {Colors.OKBLUE}[3]{Colors.ENDC} {Colors.BOLD}5 runs{Colors.ENDC} - Good statistics")
        print(f"  {Colors.OKBLUE}[4]{Colors.ENDC} {Colors.BOLD}10 runs{Colors.ENDC} - Excellent statistics")
        print(f"  {Colors.OKBLUE}[5]{Colors.ENDC} {Colors.BOLD}Custom{Colors.ENDC} - Enter custom number")
        
        print(f"\n  {Colors.YELLOW}💡 Tip: Press Enter for default (1 run){Colors.ENDC}")
        
        run_options = {'1': 1, '2': 3, '3': 5, '4': 10}
        
        while True:
            choice = input(f"\n{Colors.BOLD}➤ Enter your choice (1-5 or Enter for default): {Colors.ENDC}").strip()
            
            if not choice:  # Default
                runs = 1
                print(f"  {Colors.OKGREEN}✓ Using default: {runs} run{Colors.ENDC}")
                return runs
            elif choice in run_options:
                runs = run_options[choice]
                print(f"  {Colors.OKGREEN}✓ Selected: {runs} run{'s' if runs > 1 else ''}{Colors.ENDC}")
                return runs
            elif choice == '5':  # Custom
                try:
                    runs = int(input(f"  {Colors.BOLD}➤ Enter number of runs: {Colors.ENDC}").strip())
                    if runs > 0:
                        print(f"  {Colors.OKGREEN}✓ Custom runs: {runs}{Colors.ENDC}")
                        return runs
                    else:
                        print(f"  {Colors.FAIL}✗ Please enter a positive number.{Colors.ENDC}")
                except ValueError:
                    print(f"  {Colors.FAIL}✗ Please enter a valid number.{Colors.ENDC}")
            else:
                print(f"  {Colors.FAIL}✗ Invalid choice. Please enter 1-5 or press Enter.{Colors.ENDC}")
                
    def print_summary(self, config: Dict[str, Any]):
        """Print configuration summary."""
        print(f"\n{Colors.HEADER}{'='*self.terminal_width}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}📋 BENCHMARK CONFIGURATION SUMMARY{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*self.terminal_width}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}Primary Compiler:{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}├─{Colors.ENDC} Name: {Colors.OKGREEN}{config['compiler1']}{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}├─{Colors.ENDC} Version: {Colors.OKGREEN}{config['version1']}{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}└─{Colors.ENDC} Optimization: {Colors.OKGREEN}Level {config['opt1']}{Colors.ENDC}")
        
        if config.get('compiler2'):
            print(f"\n{Colors.BOLD}Secondary Compiler:{Colors.ENDC}")
            print(f"  {Colors.OKBLUE}├─{Colors.ENDC} Name: {Colors.OKGREEN}{config['compiler2']}{Colors.ENDC}")
            print(f"  {Colors.OKBLUE}├─{Colors.ENDC} Version: {Colors.OKGREEN}{config['version2']}{Colors.ENDC}")
            print(f"  {Colors.OKBLUE}└─{Colors.ENDC} Optimization: {Colors.OKGREEN}Level {config['opt2']}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}Benchmark Settings:{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}├─{Colors.ENDC} Backend: {Colors.OKGREEN}{config['backend']}{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}└─{Colors.ENDC} Runs per benchmark: {Colors.OKGREEN}{config['num_runs']}{Colors.ENDC}")
        
        print(f"\n{Colors.HEADER}{'-'*self.terminal_width}{Colors.ENDC}")
        
        while True:
            confirm = input(f"\n{Colors.BOLD}➤ Proceed with benchmarking? (Y/n): {Colors.ENDC}").strip().lower()
            
            if not confirm or confirm in ['y', 'yes']:
                print(f"  {Colors.OKGREEN}✓ Starting benchmark...{Colors.ENDC}")
                return True
            elif confirm in ['n', 'no']:
                print(f"  {Colors.WARNING}✗ Benchmark cancelled{Colors.ENDC}")
                return False
            else:
                print(f"  {Colors.FAIL}✗ Please enter Y or N.{Colors.ENDC}")
                
    def run_interactive_setup(self) -> Dict[str, Any]:
        """Run the complete interactive setup."""
        self.print_welcome()
        
        # Get primary compiler
        compiler1 = self.get_compiler_choice()
        version1 = self.get_version(compiler1)
        opt1 = self.get_optimization_level(compiler1)
        
        # Get optional second compiler
        second_compiler = self.get_second_compiler()
        
        # Get backend and runs
        backend = self.get_backend()
        num_runs = self.get_num_runs()
        
        # Build configuration
        config = {
            'compiler1': compiler1,
            'version1': version1,
            'opt1': opt1,
            'backend': backend,
            'num_runs': num_runs,
        }
        
        if second_compiler:
            config.update({
                'compiler2': second_compiler['compiler'],
                'version2': second_compiler['version'],
                'opt2': second_compiler['optimization_level']
            })
        
        # Show summary and confirm
        if self.print_summary(config):
            return config
        else:
            sys.exit(0)


def main():
    """Main CLI entry point."""
    try:
        cli = BeautifulCLI()
        config = cli.run_interactive_setup()
        
        # Output configuration for shell script
        config_output = f"""# Configuration for shell script:
COMPILER1={config['compiler1']}
VERSION1={config['version1']}
OPT1={config['opt1']}
BACKEND={config['backend']}
NUM_RUNS={config['num_runs']}
COMPILER2={config.get('compiler2', '')}"""
        
        if config.get('compiler2'):
            config_output += f"""
VERSION2={config['version2']}
OPT2={config['opt2']}"""
        else:
            config_output += f"""
VERSION2=
OPT2="""
        
        # Write config to a file for the shell script to read
        with open('/tmp/rq_config.txt', 'w') as f:
            f.write(config_output)
            
        print(f"\n{Colors.OKGREEN}✅ Configuration saved! Starting benchmarking...{Colors.ENDC}")
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Benchmark setup interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Error: {str(e)}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
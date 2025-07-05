"""
Beautiful progress visualizer for Red Queen benchmarking.
"""

import sys
import time
import os
from datetime import datetime
from typing import Dict, List, Optional, Any


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
    
    # Additional colors
    PURPLE = '\033[35m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'


class ProgressVisualizer:
    """Beautiful terminal progress visualizer for benchmarking."""
    
    def __init__(self, total_benchmarks: int, num_runs: int, compiler_info: Dict[str, Any]):
        self.total_benchmarks = total_benchmarks
        self.num_runs = num_runs
        self.total_operations = total_benchmarks * num_runs
        self.current_operation = 0
        self.compiler_info = compiler_info
        self.start_time = None
        self.current_benchmark = None
        self.current_run = 0
        self.benchmark_results = {}
        
        # Terminal width for progress bar
        try:
            self.terminal_width = min(os.get_terminal_size().columns, 120)
        except OSError:
            # Handle case where stdout is redirected or not a terminal
            self.terminal_width = 80
        self.progress_bar_width = max(40, self.terminal_width - 50)
        
    def print_header(self):
        """Print beautiful header with benchmark information."""
        print(f"\n{Colors.HEADER}{'='*self.terminal_width}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}🚀 RED QUEEN QUANTUM BENCHMARKING SUITE 🚀{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*self.terminal_width}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}📊 Benchmark Configuration:{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}├─{Colors.ENDC} Compiler: {Colors.OKGREEN}{self.compiler_info['compiler']}{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}├─{Colors.ENDC} Version: {Colors.OKGREEN}{self.compiler_info['version']}{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}├─{Colors.ENDC} Optimization Level: {Colors.OKGREEN}{self.compiler_info['optimization_level']}{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}├─{Colors.ENDC} Total Benchmarks: {Colors.OKGREEN}{self.total_benchmarks}{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}├─{Colors.ENDC} Runs per Benchmark: {Colors.OKGREEN}{self.num_runs}{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}└─{Colors.ENDC} Total Operations: {Colors.OKGREEN}{self.total_operations}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}🕐 Started at: {Colors.ENDC}{Colors.CYAN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'-'*self.terminal_width}{Colors.ENDC}\n")
        
    def start_benchmarking(self):
        """Start the benchmarking process."""
        self.start_time = time.time()
        self.print_header()
        
    def start_benchmark(self, benchmark_name: str):
        """Start processing a new benchmark."""
        self.current_benchmark = benchmark_name
        self.current_run = 0
        print(f"\n{Colors.BOLD}{Colors.PURPLE}🔬 Processing: {benchmark_name}{Colors.ENDC}")
        
    def start_run(self, run_number: int):
        """Start a new run of the current benchmark."""
        self.current_run = run_number
        self.current_operation += 1
        
    def update_progress(self, stage: str, stage_color: str = Colors.OKBLUE):
        """Update progress with current stage."""
        progress = self.current_operation / self.total_operations
        filled_length = int(self.progress_bar_width * progress)
        
        # Create progress bar
        bar = '█' * filled_length + '░' * (self.progress_bar_width - filled_length)
        percentage = progress * 100
        
        # Calculate time estimates
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        if progress > 0:
            eta = (elapsed_time / progress) * (1 - progress)
            eta_str = self._format_time(eta)
        else:
            eta_str = "calculating..."
            
        # Clear line and print progress
        print(f"\r{Colors.GRAY}[{Colors.ENDC}{Colors.OKGREEN}{bar}{Colors.ENDC}{Colors.GRAY}]{Colors.ENDC} "
              f"{Colors.BOLD}{percentage:5.1f}%{Colors.ENDC} "
              f"{Colors.GRAY}|{Colors.ENDC} {stage_color}{stage}{Colors.ENDC} "
              f"{Colors.GRAY}| ETA: {eta_str}{Colors.ENDC}", end='', flush=True)
        
    def log_stage(self, stage: str, benchmark_name: str = None, details: str = None):
        """Log a stage with beautiful formatting."""
        if benchmark_name:
            print(f"\n  {Colors.OKBLUE}├─{Colors.ENDC} {Colors.BOLD}{stage}{Colors.ENDC} "
                  f"{Colors.GRAY}({benchmark_name}){Colors.ENDC}")
        else:
            print(f"\n  {Colors.OKBLUE}├─{Colors.ENDC} {Colors.BOLD}{stage}{Colors.ENDC}")
            
        if details:
            print(f"  {Colors.OKBLUE}│  {Colors.ENDC}{Colors.GRAY}{details}{Colors.ENDC}")
            
    def complete_benchmark(self, benchmark_name: str, results: Dict[str, Any]):
        """Complete a benchmark and show results."""
        self.benchmark_results[benchmark_name] = results
        
        print(f"\n  {Colors.OKGREEN}✅ Completed: {benchmark_name}{Colors.ENDC}")
        
        # Show quick stats if available
        if 'aggregate' in results:
            agg = results['aggregate']
            if 'total_time (seconds)' in agg:
                avg_time = agg['total_time (seconds)']['mean']
                print(f"  {Colors.GRAY}└─ Avg Time: {avg_time:.3f}s{Colors.ENDC}")
                
    def print_summary(self):
        """Print beautiful summary of all results."""
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        
        print(f"\n\n{Colors.HEADER}{'='*self.terminal_width}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.OKGREEN}🎉 BENCHMARKING COMPLETE! 🎉{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*self.terminal_width}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}📈 Summary Statistics:{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}├─{Colors.ENDC} Total Time: {Colors.OKGREEN}{self._format_time(elapsed_time)}{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}├─{Colors.ENDC} Benchmarks Processed: {Colors.OKGREEN}{len(self.benchmark_results)}{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}├─{Colors.ENDC} Total Operations: {Colors.OKGREEN}{self.total_operations}{Colors.ENDC}")
        print(f"  {Colors.OKBLUE}└─{Colors.ENDC} Avg Time per Operation: {Colors.OKGREEN}{elapsed_time/self.total_operations:.3f}s{Colors.ENDC}")
        
        # Show top performing benchmarks
        if self.benchmark_results:
            print(f"\n{Colors.BOLD}🏆 Performance Highlights:{Colors.ENDC}")
            
            # Sort by average total time
            sorted_benchmarks = []
            for name, results in self.benchmark_results.items():
                if 'aggregate' in results and 'total_time (seconds)' in results['aggregate']:
                    avg_time = results['aggregate']['total_time (seconds)']['mean']
                    sorted_benchmarks.append((name, avg_time))
            
            sorted_benchmarks.sort(key=lambda x: x[1])
            
            # Show fastest and slowest
            if len(sorted_benchmarks) >= 1:
                fastest = sorted_benchmarks[0]
                print(f"  {Colors.OKGREEN}🚀 Fastest: {fastest[0]} ({fastest[1]:.3f}s){Colors.ENDC}")
                
            if len(sorted_benchmarks) >= 2:
                slowest = sorted_benchmarks[-1]
                print(f"  {Colors.WARNING}🐌 Slowest: {slowest[0]} ({slowest[1]:.3f}s){Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}💾 Results saved to: {Colors.ENDC}{Colors.CYAN}results/ directory{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*self.terminal_width}{Colors.ENDC}\n")
        
    def print_detailed_results(self, benchmark_name: str, results: Dict[str, Any]):
        """Print detailed results for a benchmark in a beautiful format."""
        print(f"\n{Colors.BOLD}{Colors.PURPLE}📊 Detailed Results: {benchmark_name}{Colors.ENDC}")
        print(f"{Colors.PURPLE}{'─'*50}{Colors.ENDC}")
        
        if 'aggregate' in results:
            agg = results['aggregate']
            
            metrics = [
                ('Total Time', 'total_time (seconds)', 's'),
                ('Transpile Time', 'transpile_time (seconds)', 's'),
                ('Memory Usage', 'memory_footprint (MiB)', 'MiB'),
                ('Circuit Depth', 'depth (gates)', 'gates')
            ]
            
            for display_name, metric_key, unit in metrics:
                if metric_key in agg:
                    data = agg[metric_key]
                    print(f"  {Colors.OKBLUE}{display_name:15}{Colors.ENDC}")
                    print(f"    {Colors.GRAY}Mean:{Colors.ENDC} {Colors.OKGREEN}{data['mean']:.4f} {unit}{Colors.ENDC}")
                    print(f"    {Colors.GRAY}Median:{Colors.ENDC} {Colors.OKGREEN}{data['median']:.4f} {unit}{Colors.ENDC}")
                    print(f"    {Colors.GRAY}Std Dev:{Colors.ENDC} {Colors.OKGREEN}{data['standard_deviation']:.4f} {unit}{Colors.ENDC}")
                    print()
        
    def _format_time(self, seconds: float) -> str:
        """Format time in a human-readable way."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.1f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60
            return f"{hours}h {minutes}m {secs:.1f}s"
            
    def error(self, message: str):
        """Display an error message."""
        print(f"\n{Colors.FAIL}❌ Error: {message}{Colors.ENDC}")
        
    def warning(self, message: str):
        """Display a warning message."""
        print(f"\n{Colors.WARNING}⚠️  Warning: {message}{Colors.ENDC}")
        
    def info(self, message: str):
        """Display an info message."""
        print(f"\n{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}") 
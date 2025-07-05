#!/bin/bash

# Beautiful Red Queen Benchmarking Script
# This script provides a modern, user-friendly CLI interface

# Check if Python CLI interface exists
if [ ! -f "cli_interface.py" ]; then
    echo "Error: cli_interface.py not found!"
    exit 1
fi

# Make CLI interface executable
chmod +x cli_interface.py

# Run the beautiful CLI interface and capture configuration
echo "Starting Red Queen Benchmarking Suite..."

# Run the CLI interface
python3 cli_interface.py
cli_exit_code=$?

# Check if CLI was successful
if [ $cli_exit_code -ne 0 ]; then
    echo "Setup cancelled or failed. Exit code: $cli_exit_code"
    exit 1
fi

# Read configuration from the file created by CLI
if [ -f "/tmp/rq_config.txt" ]; then
    source /tmp/rq_config.txt
    rm /tmp/rq_config.txt
    echo "Configuration loaded successfully!"
else
    echo "Error: Configuration file not found!"
    exit 1
fi

# Function to setup and run virtual environment
venv_spinup () {
    # Naming convention: venv_compilerName_versionNumber
    venv_name="venv_${1}_$2"
    
    # Create virtual_environments directory if it doesn't exist
    if [ ! -d "virtual_environments" ]; then
        mkdir virtual_environments
    fi
    
    cd virtual_environments
    
    if [ -d "$venv_name" ]; then
        echo "🔄 Activating existing virtual environment: $venv_name"
        source $venv_name/bin/activate
    else
        echo "🆕 Creating new virtual environment: $venv_name"
        python3 -m venv $venv_name
        source $venv_name/bin/activate
        
        echo "📦 Installing dependencies..."
        pip install --quiet memory_profiler numpy
        
        if [ "$1" = "pytket" ]; then
            echo "Installing PyTKET $2..."
            if ! pip install --quiet pytket==$2; then
                echo "❌ Failed to install pytket==$2"
                echo "💡 Available versions: $(pip index versions pytket 2>/dev/null | head -5 | tail -4 || echo 'Check PyPI for available versions')"
                exit 1
            fi
            echo "Installing Qiskit for compatibility..."
            if ! pip install --quiet qiskit; then
                echo "⚠️  Warning: Failed to install qiskit for compatibility"
            fi
        elif [ "$1" = "qiskit" ]; then
            echo "Installing Qiskit $2..."
            if ! pip install --quiet qiskit==$2; then
                echo "❌ Failed to install qiskit==$2"
                echo "💡 Available versions: $(pip index versions qiskit 2>/dev/null | head -5 | tail -4 || echo 'Check PyPI for available versions')"
                exit 1
            fi
            echo "Installing PyTKET for compatibility..."
            if ! pip install --quiet pytket; then
                echo "⚠️  Warning: Failed to install pytket for compatibility"
            fi
        fi
        
        echo "✅ Virtual environment setup complete!"
    fi

    cd ..
    
    # Run the benchmarking
    echo "🚀 Starting benchmarking process..."
    python3 runner.py $1 $2 $3 $4 $5 $6 
    
    deactivate
}

# Run primary compiler
echo "🔧 Setting up primary compiler environment..."
second_compiler_readout=false
venv_spinup $COMPILER1 $VERSION1 $OPT1 $BACKEND $NUM_RUNS $second_compiler_readout

# Run secondary compiler if specified
if [ -n "$COMPILER2" ]; then
    echo "🔧 Setting up secondary compiler environment..."
    second_compiler_readout=true
    venv_spinup $COMPILER2 $VERSION2 $OPT2 $BACKEND $NUM_RUNS $second_compiler_readout
fi

echo "🎉 Benchmarking complete! Check the results directory for output files." 
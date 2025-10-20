import os
import subprocess
import sys
import platform

def compile_sm64():
    # Prompt the user for the path to the SM64 source code directory
    source_dir = input("Enter the path to the SM64 source code directory: ")

    # Check if the source code directory exists
    if not os.path.isdir(source_dir):
        print("Error: The specified source code directory does not exist.")
        return

    # Prompt the user for the path to the base ROM
    base_rom_path = input("Enter the path to the base ROM (e.g., baserom.us.z64): ")

    # Check if the base ROM exists
    if not os.path.isfile(base_rom_path):
        print("Error: The specified base ROM file does not exist.")
        return

    # Prompt the user for the desired version (US, JP, or EU)
    version = input("Enter the desired version (us, jp, or eu): ")

    # Check if the selected version is valid
    if version not in ['us', 'jp', 'eu']:
        print('Invalid version. Please choose "us", "jp", or "eu".')
        return

    # Change to the SM64 source code directory
    os.chdir(source_dir)

    # Set up the environment for the selected version
    os.environ['VERSION'] = version

    # Copy the base ROM to the source directory
    subprocess.run(['cp', base_rom_path, f'baserom.{version}.z64'])

    # Compile the SM64 source code and handle potential errors
    try:
        subprocess.check_call(['make'])
        print(f'Successfully compiled SM64 ({version}) into build/{version}_pc/sm64.{version}.z64')
    except subprocess.CalledProcessError as e:
        print(f'Error: Compilation failed with exit code {e.returncode}.')
        return

if __name__ == '__main__':
    # Check the operating system for compatibility
    os_name = platform.system()
    if os_name not in ['Windows', 'Darwin', 'Linux']:
        print('Error: This script is only compatible with Windows, macOS, and Linux.')
        sys.exit(1)

    # Check if the system is running on an ARM-based Mac (M1 Mac)
    if os_name == 'Darwin' and platform.processor() == 'arm':
        print('Warning: You are running on an ARM-based Mac (M1 Mac). Please ensure you have the necessary tools and dependencies installed for ARM architecture.')

    # Run the compilation process
    compile_sm64()

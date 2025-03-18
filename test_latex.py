#!/usr/bin/env python3
"""
Test script to verify LaTeX generation functionality
"""
import json
import os
from server import generate_latex_code, INDIAN_SCRIPT_DIGITS, FONT_MAPPING

def create_test_data():
    """Create a small test dataset with just a few cells"""
    # Create a small 3x3 grid
    grid = []
    for i in range(3):
        row = []
        for j in range(3):
            cell = {
                "digit": "3" if i == 0 and j == 0 else str((i*3 + j) % 9 + 1),
                "script": "Latin" if i == 0 and j == 0 else list(INDIAN_SCRIPT_DIGITS.keys())[((i*3 + j) % len(INDIAN_SCRIPT_DIGITS))],
                "value": "3" if i == 0 and j == 0 else str((i*3 + j) % 9 + 1),
                "highlight": (i == 1 and j == 1)  # Center cell highlighted
            }
            row.append(cell)
        grid.append(row)
    
    # Create the full data object
    test_data = {
        "grid": grid,
        "rows": 3,
        "cols": 3,
        "num_digits": 9,
        "seed": 42,
        "script_usage": {script: 0 for script in INDIAN_SCRIPT_DIGITS.keys()},
        "total_scripts_used": len(INDIAN_SCRIPT_DIGITS)
    }
    
    # Update script usage counts
    for row in grid:
        for cell in row:
            test_data["script_usage"][cell["script"]] += 1
    
    return test_data

def main():
    # Create test data
    test_data = create_test_data()
    
    # Save test data to file for reference
    with open("test_data.json", "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print("Generated test data with a 3x3 grid")
    
    # Generate LaTeX code
    latex_code = generate_latex_code(test_data, "LaTeX Test")
    
    # Save LaTeX to file
    with open("test_latex.tex", "w", encoding="utf-8") as f:
        f.write(latex_code)
    
    print("Generated LaTeX code and saved to test_latex.tex")
    
    # Create fonts directory if it doesn't exist
    if not os.path.exists("fonts"):
        os.makedirs("fonts")
        print("Created fonts directory. Please add font files there.")
    
    print("\nTest completed successfully!")
    print("To verify, check the generated LaTeX file: test_latex.tex")

if __name__ == "__main__":
    main() 
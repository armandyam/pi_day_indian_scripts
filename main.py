import unicodedata
import math
import random
import mpmath
import json
import numpy as np
from PIL import Image, ImageDraw

# Set precision for pi calculation
mpmath.mp.dps = 1000  # Set precision to 1000 digits

# Unicode numeral scripts with starting code points for digits (0-9)
# Only including Indian scripts as specified
NUMERAL_SCRIPTS = {
    # Indian scripts
    "Assamese": 0x09E6,  # Same as Bengali
    "Bengali": 0x09E6,
    "Devanagari": 0x0966,  # Used for Hindi, Sanskrit, Marathi, Bodo, Dogri, Konkani, Maithili, Nepali
    "Gujarati": 0x0AE6,
    "Gurmukhi": 0x0A66,  # Used for Punjabi
    "Kannada": 0x0CE6,
    "Malayalam": 0x0D66,
    "Odia": 0x0B66,  # Formerly known as Oriya
    "Ol Chiki": 0x1C50,  # Used for Santali
    "Tamil": 0x0BE6,
    "Telugu": 0x0C66,
    "Urdu": 0x06F0,  # Uses Extended Arabic-Indic digits
    "Kashmiri": 0x06F0,  # Uses Perso-Arabic script (Extended Arabic-Indic digits)
    "Sindhi": 0x06F0,  # Uses Perso-Arabic script (Extended Arabic-Indic digits)
    "Manipuri": 0xABF0,  # Meetei Mayek script
    
    # Add Latin for English
    "Latin": 0x0030,
}

# Scripts that are well-supported in most LaTeX distributions and browsers
WELL_SUPPORTED_SCRIPTS = [
    "Latin", "Devanagari", "Bengali", "Assamese", "Gujarati", 
    "Gurmukhi", "Tamil", "Telugu", "Kannada", "Malayalam", 
    "Odia", "Urdu", "Kashmiri", "Sindhi", "Manipuri", "Ol Chiki"
]

# Constants for grid configuration and constraints
MIN_DIGITS = 10
MAX_DIGITS = 1000
A4_RATIO = 1.414  # A4 page ratio (height/width)

# A4 paper dimensions in points
A4_WIDTH_PT = 597.0  # 21 cm or 210 mm
A4_HEIGHT_PT = 842.0  # 29.7 cm or 297 mm

# Layout parameters
TOP_MARGIN_PT = 56.9  # 2 cm
BOTTOM_MARGIN_PT = 14.2  # 0.5 cm
LEFT_RIGHT_MARGIN_PT = 14.2  # 0.5 cm (was 28.3 for 1cm, now changed to 0.5cm)
TITLE_SPACE_PT = 42.0  # Space for title and padding below
FOOTER_SPACE_PT = 20.0  # Space for footer text

def calculate_grid_dimensions(num_digits):
    """
    Calculate optimal rows and columns for a given number of digits to fit an A4 page ratio.
    """
    # Ensure num_digits is within acceptable range
    num_digits = max(MIN_DIGITS, min(MAX_DIGITS, num_digits))
    
    # Calculate optimal dimensions to match A4 ratio (portrait orientation)
    # We want rows/cols ≈ A4_ratio
    cols = math.sqrt(num_digits / A4_RATIO)
    rows = num_digits / cols
    
    # Round to whole numbers, ensuring we have enough cells for the digits
    cols = max(3, round(cols))  # Minimum 3 columns
    rows = max(3, math.ceil(num_digits / cols))  # Minimum 3 rows, round up to ensure enough cells
    
    return rows, cols

def calculate_exact_font_size(rows, cols):
    """
    Calculate precise font size in points to fit digits optimally on an A4 page.
    Returns the fontsize and baselineskip values for LaTeX.
    """
    # Calculate available space on the page
    available_width = A4_WIDTH_PT - (2 * LEFT_RIGHT_MARGIN_PT)
    available_height = A4_HEIGHT_PT - TOP_MARGIN_PT - BOTTOM_MARGIN_PT - TITLE_SPACE_PT - FOOTER_SPACE_PT
    
    # Calculate cell dimensions
    cell_width = available_width / cols
    cell_height = available_height / rows
    
    # Use the smaller dimension to ensure cells remain square-ish
    # We'll use 80% of the cell dimension for the font size to provide spacing
    cell_size = min(cell_width, cell_height)
    font_size = cell_size * 0.8
    
    # baselineskip is typically 1.2 times the font size
    baseline_skip = font_size * 1.2
    
    return font_size, baseline_skip

def get_pi_digits(n=200):
    """
    Generate the first n digits of pi using mpmath for high precision.
    """
    pi_str = str(mpmath.mp.pi)
    # Keep the decimal point and take the first n+1 characters (including the decimal)
    pi_digits = pi_str[:n+1]  # Include decimal point
    return pi_digits

def convert_digit(digit, script):
    """
    Convert a single digit to the specified script.
    """
    if digit == '.':
        # Return the decimal point as is
        return '.'
    
    start_code = NUMERAL_SCRIPTS[script]
    return chr(start_code + int(digit))

def generate_pi_shape_mask(rows, cols):
    """
    Generate a mask in the shape of the π symbol.
    Returns a 2D array where True indicates a pixel that should be colored red.
    """
    # Create a blank image
    img = Image.new('1', (cols, rows), 0)
    draw = ImageDraw.Draw(img)
    
    # Calculate dimensions for the pi symbol
    width = cols * 0.7
    height = rows * 0.7
    x_offset = (cols - width) / 2
    y_offset = (rows - height) / 2
    
    # Draw the horizontal line of pi
    line_height = height * 0.2
    draw.rectangle([(x_offset, y_offset), 
                   (x_offset + width, y_offset + line_height)], fill=1)
    
    # Draw the left vertical line
    left_x = x_offset + width * 0.25
    draw.rectangle([(left_x - width * 0.1, y_offset), 
                   (left_x + width * 0.1, y_offset + height)], fill=1)
    
    # Draw the right vertical line
    right_x = x_offset + width * 0.75
    draw.rectangle([(right_x - width * 0.1, y_offset), 
                   (right_x + width * 0.1, y_offset + height)], fill=1)
    
    # Convert to numpy array
    mask = np.array(img)
    return mask

def get_valid_scripts(row, col, grid_scripts, rows, cols, used_scripts_count):
    """
    Get a list of valid scripts that don't conflict with adjacent cells,
    prioritizing scripts that have been used less frequently.
    """
    adjacent_scripts = set()
    
    # Check all 8 adjacent positions
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue  # Skip the current cell
            
            r, c = row + dr, col + dc
            if 0 <= r < rows and 0 <= c < cols and grid_scripts[r][c] is not None:
                adjacent_scripts.add(grid_scripts[r][c])
    
    # Get scripts that aren't used in adjacent cells
    valid_scripts = [script for script in NUMERAL_SCRIPTS.keys() if script not in adjacent_scripts]
    
    # Sort by usage count (prefer less used scripts)
    valid_scripts.sort(key=lambda s: used_scripts_count.get(s, 0))
    
    return valid_scripts

def create_pi_grid(rows=10, cols=20, seed=None):
    """
    Create a grid of pi digits using different scripts for adjacent cells,
    maximizing script diversity.
    """
    if seed is not None:
        random.seed(seed)
    
    pi_digits = get_pi_digits(rows * cols)
    
    # Initialize grid for scripts and digits
    grid_scripts = [[None for _ in range(cols)] for _ in range(rows)]
    grid_digits = [[None for _ in range(cols)] for _ in range(rows)]
    
    # Generate pi shape mask for colored cells
    pi_mask = generate_pi_shape_mask(rows, cols)
    
    # Track script usage
    used_scripts_count = {script: 0 for script in NUMERAL_SCRIPTS.keys()}
    
    # Set first digit to Latin "3"
    grid_scripts[0][0] = "Latin"
    grid_digits[0][0] = "3"
    used_scripts_count["Latin"] += 1
    
    # Set second position to decimal point (keep it as a period)
    grid_scripts[0][1] = "Latin"
    grid_digits[0][1] = "."
    used_scripts_count["Latin"] += 1
    
    # Fill the rest of the grid
    for row in range(rows):
        for col in range(cols):
            # Skip the first two positions (already filled)
            if (row == 0 and col == 0) or (row == 0 and col == 1):
                continue
                
            index = row * cols + col
            if index < len(pi_digits):
                digit = pi_digits[index]
            else:
                # If we run out of digits, use 0
                digit = "0"
            
            # Skip if it's a decimal point (already handled)
            if digit == '.':
                continue
                
            # Get valid scripts for this position, prioritizing less used scripts
            valid_scripts = get_valid_scripts(row, col, grid_scripts, rows, cols, used_scripts_count)
            
            # For better browser compatibility, prefer well-supported scripts
            well_supported = [s for s in valid_scripts if s in WELL_SUPPORTED_SCRIPTS]
            if well_supported:
                valid_scripts = well_supported + [s for s in valid_scripts if s not in WELL_SUPPORTED_SCRIPTS]
            
            if not valid_scripts:
                # If no valid scripts, use any script (this shouldn't happen with 15+ scripts)
                valid_scripts = list(NUMERAL_SCRIPTS.keys())
            
            # Choose a script from valid options, preferring less used ones
            chosen_script = valid_scripts[0]  # Take the least used script
            
            # Store the script and convert the digit
            grid_scripts[row][col] = chosen_script
            grid_digits[row][col] = convert_digit(digit, chosen_script)
            
            # Update usage count
            used_scripts_count[chosen_script] += 1
    
    # Calculate script diversity statistics
    script_usage = {script: count for script, count in used_scripts_count.items() if count > 0}
    total_scripts_used = len(script_usage)
    
    return grid_digits, grid_scripts, script_usage, total_scripts_used, pi_mask

def generate_latex(grid_digits, grid_scripts, rows=10, cols=20, title="π in Indian Scripts", pi_mask=None):
    """
    Generate LaTeX code for the pi grid.
    """
    latex = []
    latex.append(r"\documentclass[12pt]{article}")
    latex.append(r"\usepackage[a4paper, top=2cm, left=0.5cm, right=0.5cm, bottom=0.5cm]{geometry} % Margins: top=2cm, left/right=0.5cm, bottom=0.5cm")
    latex.append(r"\usepackage{fontspec}")
    latex.append(r"\usepackage{xcolor}")
    latex.append(r"\usepackage{tikz}")
    latex.append(r"\usepackage{array}")
    latex.append(r"\usepackage{colortbl}")
    latex.append(r"\usepackage{multicol}")
    latex.append(r"\usepackage{fancyhdr}")
    latex.append(r"\usepackage{graphicx}")
    latex.append(r"\usepackage{lmodern}")  # Add lmodern for better font scaling
    
    # Set up fonts
    latex.append(r"\setmainfont{Noto Sans}")
    
    # Define colors
    latex.append(r"\definecolor{bg}{RGB}{252, 252, 252}")
    latex.append(r"\definecolor{gridline}{RGB}{220, 220, 220}")
    latex.append(r"\definecolor{title}{RGB}{50, 50, 50}")
    latex.append(r"\definecolor{highlight}{RGB}{231, 76, 60}")  # Red color for pi shape
    
    # Page setup
    latex.append(r"\pagestyle{fancy}")
    latex.append(r"\fancyhf{}")
    latex.append(r"\renewcommand{\headrulewidth}{0pt}")
    latex.append(r"\renewcommand{\footrulewidth}{0pt}")
    latex.append(r"\fancyfoot[C]{\thepage}")
    
    # Background color
    latex.append(r"\pagecolor{bg}")
    latex.append(r"\pagecolor{white} % White background")

    # Begin document
    latex.append(r"\begin{document}")
    latex.append(r"\thispagestyle{empty} % Remove page number")
    
    # Title
    latex.append(r"\begin{center}")
    latex.append(r"{\Huge\textbf{" + title + r"}}")
    latex.append(r"\vspace{0.5cm}")
    latex.append(r"\end{center}")
    
    # Calculate precise font size to fit the grid on the page
    # Calculate a fresh font size each time to ensure we use current LEFT_RIGHT_MARGIN_PT value
    font_size, baseline_skip = calculate_exact_font_size(rows, cols)
    font_size_cmd = f"\\fontsize{{{font_size:.1f}pt}}{{{baseline_skip:.1f}pt}}\\selectfont"
    
    # Create a table for the grid
    latex.append(r"\begin{center}")
    latex.append(r"\begin{tikzpicture}")
    
    # Draw grid background
    latex.append(r"\draw[fill=white, draw=none] (0,0) rectangle (" + str(cols) + "," + str(rows) + ");")
    
    # Place digits
    for row in range(rows):
        for col in range(cols):
            # Get the digit and script
            digit_char = grid_digits[row][col]
            script = grid_scripts[row][col]
            
            # Calculate position (center of cell)
            x = col + 0.5
            y = rows - row - 0.5  # Invert y-axis for LaTeX
            
            # Check if this cell should be highlighted (in pi shape)
            if pi_mask is not None and pi_mask[row][col]:
                color_cmd = r"\textcolor{highlight}"
            else:
                color_cmd = ""
            
            # Add the digit with proper script, color, and font size
            if script == "Latin" and digit_char == ".":
                # Handle decimal point specially
                latex.append(r"\node at (" + f"{x},{y}" + r") {" + color_cmd + r"{" + font_size_cmd + r" .}};")
            else:
                # Fix the script variable issue by using proper string formatting
                font_name = "Noto Sans"
                if script in ["Urdu", "Kashmiri", "Sindhi"]:
                    font_name = "Noto Sans Arabic"
                elif script == "Assamese":
                    font_name = "Noto Sans Bengali"
                elif script == "Manipuri":
                    font_name = "Noto Sans Meetei Mayek"
                elif script == "Odia":
                    font_name = "Noto Sans Oriya"
                elif script == "Latin":
                    font_name = "Noto Sans"
                else:
                    font_name = f"Noto Sans {script}"
                
                latex.append(r"\node at (" + f"{x},{y}" + r") {" + color_cmd + r"{\fontspec{" + font_name + "}" + font_size_cmd + r" " + digit_char + r"}};")
    
    latex.append(r"\end{tikzpicture}")
    latex.append(r"\end{center}")
    
    # Add legend for scripts
    latex.append(r"\vspace{1cm}")
    
    # Get unique scripts used
    used_scripts = set()
    for row in grid_scripts:
        for script in row:
            if script:  # Only add if script is not None
                used_scripts.add(script)
    
    # Sort scripts alphabetically
    used_scripts = sorted(list(used_scripts))
    
    # Add footer with information
    latex.append(r"\vfill")
    latex.append(r"\begin{center}")
    latex.append(r"\tiny{This poster displays the first " + str(rows * cols) + r" digits of π using " + str(len(used_scripts)) + r" different Indian numeral scripts.}")
    latex.append(r"\end{center}")
    
    # End document
    latex.append(r"\end{document}")
    
    return "\n".join(latex)

def generate_json_data(num_digits=200, seed=None):
    """
    Generate JSON data for the web interface based on number of digits.
    """
    # Calculate optimal rows and columns for this number of digits
    rows, cols = calculate_grid_dimensions(num_digits)
    
    grid_digits, grid_scripts, script_usage, total_scripts_used, pi_mask = create_pi_grid(rows, cols, seed)
    
    # Convert grid data to format suitable for JSON
    grid_data = []
    for row in range(rows):
        row_data = []
        for col in range(cols):
            cell = {
                "digit": grid_digits[row][col],
                "script": grid_scripts[row][col],
                "unicode": hex(ord(grid_digits[row][col])) if grid_digits[row][col] != '.' else "0x2E",
                "highlight": bool(pi_mask[row][col])  # Add highlight flag for pi shape
            }
            row_data.append(cell)
        grid_data.append(row_data)
    
    # Create JSON object
    data = {
        "grid": grid_data,
        "script_usage": script_usage,
        "total_scripts_used": total_scripts_used,
        "rows": rows,
        "cols": cols,
        "num_digits": num_digits,
        "seed": seed if seed is not None else random.randint(1, 1000000)
    }
    
    return json.dumps(data, indent=2)

def main():
    # Set random seed for reproducibility (or use None for random)
    seed = 42
    
    # Set number of digits and calculate optimal grid dimensions
    num_digits = 200
    rows, cols = calculate_grid_dimensions(num_digits)
    
    # Create the pi grid
    grid_digits, grid_scripts, script_usage, total_scripts_used, pi_mask = create_pi_grid(rows, cols, seed)
    
    # Print the result
    print(f"Pi Visualization ({num_digits} digits in a {rows}x{cols} grid) using {total_scripts_used} different Indian scripts:")
    for row in grid_digits:
        print("".join(row))
    
    # Generate LaTeX code
    latex_code = generate_latex(grid_digits, grid_scripts, rows, cols, pi_mask=pi_mask)
    
    # Save LaTeX to file
    with open("pi_visualization.tex", "w", encoding="utf-8") as f:
        f.write(latex_code)
    
    # Generate JSON data for web interface
    json_data = generate_json_data(num_digits, seed)
    
    # Save JSON to file
    with open("pi_data.json", "w", encoding="utf-8") as f:
        f.write(json_data)
    
    print(f"\nLaTeX file generated: pi_visualization.tex")
    print(f"JSON data generated: pi_data.json")
    print(f"\nTotal scripts used: {total_scripts_used}")
    print("Script usage statistics:")
    for script, count in sorted(script_usage.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {script}: {count}")

if __name__ == "__main__":
    main()

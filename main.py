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
MAX_DIGITS = 440
A4_RATIO = 1.414  # A4 page ratio (height/width)

# A4 paper dimensions in points
A4_WIDTH_PT = 597.0  # 21 cm or 210 mm
A4_HEIGHT_PT = 842.0  # 29.7 cm or 297 mm

# Layout parameters
TOP_MARGIN_PT = 56.9  # 2 cm
BOTTOM_MARGIN_PT = 14.2  # 0.5 cm
LEFT_RIGHT_MARGIN_PT = 5.0  # Reduced to 0.18 cm (was 28.3 for 1cm)
TITLE_SPACE_PT = 42.0  # Space for title and padding below
FOOTER_SPACE_PT = 20.0  # Space for footer text

def calculate_grid_dimensions(num_digits):
    """
    Calculate optimal rows and columns for a given number of digits to fit an A4 page ratio.
    """
    # Ensure num_digits is within acceptable range
    num_digits = max(MIN_DIGITS, min(MAX_DIGITS, num_digits))
    
    # Calculate the actual available space dimensions after accounting for margins
    available_width = A4_WIDTH_PT - (2 * LEFT_RIGHT_MARGIN_PT)
    available_height = A4_HEIGHT_PT - TOP_MARGIN_PT - BOTTOM_MARGIN_PT - TITLE_SPACE_PT - FOOTER_SPACE_PT
    
    # Calculate the actual ratio based on available space
    actual_ratio = available_height / available_width
    
    # Calculate optimal dimensions to match the actual available space ratio (portrait orientation)
    # We want rows/cols ≈ actual_ratio
    cols = math.sqrt(num_digits / actual_ratio)
    rows = num_digits / cols
    
    # Round to whole numbers, ensuring we have enough cells for the digits
    cols = max(3, round(cols))  # Minimum 3 columns
    rows = max(3, math.ceil(num_digits / cols))  # Minimum 3 rows, round up to ensure enough cells
    
    print(f"Available space ratio: {actual_ratio:.3f} (vs A4 ratio: {A4_RATIO:.3f})")
    print(f"Grid dimensions: {rows} rows x {cols} columns")
    return rows, cols

def calculate_exact_font_size(rows, cols, left_right_margin_pt=LEFT_RIGHT_MARGIN_PT):
    """
    Calculate precise font size in points to fit digits optimally on an A4 page.
    Returns the fontsize and baselineskip values for LaTeX.
    """
    # Calculate available space on the page
    available_width = A4_WIDTH_PT - (2 * left_right_margin_pt)
    available_height = A4_HEIGHT_PT - TOP_MARGIN_PT - BOTTOM_MARGIN_PT - TITLE_SPACE_PT - FOOTER_SPACE_PT
    
    # Calculate cell dimensions with scaling for larger grids
    cell_scale = min(1.0, 30.0/max(rows, cols))  # Scale down for larger grids
    
    cell_width = available_width / cols
    cell_height = available_height / rows
    
    # Use the smaller dimension to ensure cells remain square-ish
    # Increase the percentage for larger grids to reduce whitespace
    cell_size = min(cell_width, cell_height)
    font_percentage = min(0.9, 0.7 + 0.2 * (1 - cell_scale))  # Larger font percentage to reduce whitespace
    font_size = cell_size * font_percentage
    
    # Reduced baseline skip to decrease vertical spacing
    baseline_skip = font_size * 1.05  # Reduced from 1.2 to 1.05
    print(font_size, baseline_skip, left_right_margin_pt, cols, rows, cell_scale)
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

def create_pi_grid(rows=10, cols=20, seed=None, sampling_strategy="random", script_weights=None):
    """
    Create a grid of pi digits using different scripts for adjacent cells.
    
    Parameters:
    -----------
    rows, cols : int
        Dimensions of the grid
    seed : int or None
        Random seed for reproducibility
    sampling_strategy : str
        How to choose scripts - "random", "least_used", or "weighted"
    script_weights : dict or None
        If sampling_strategy is "weighted", use these weights for each script
    """
    # Always set a random seed - either the provided one or a new random one
    if seed is not None:
        # Explicitly convert to int in case it's a string or float
        try:
            seed_int = int(seed)
            random.seed(seed_int)
            print(f"Using seed: {seed_int}")
        except (ValueError, TypeError):
            # If conversion fails, generate a new random seed
            seed_int = random.randint(1, 1000000)
            random.seed(seed_int)
            print(f"Invalid seed provided, using random seed: {seed_int}")
    else:
        # Generate a reproducible random seed
        seed_int = random.randint(1, 1000000)
        random.seed(seed_int)
        print(f"No seed provided, using random seed: {seed_int}")

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
    
    # Default weights for weighted sampling if none provided
    if script_weights is None:
        script_weights = {script: 1.0 for script in NUMERAL_SCRIPTS.keys()}
    
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
            
            # Get valid scripts for this position (those not already in adjacent cells)
            valid_scripts = get_valid_scripts(row, col, grid_scripts, rows, cols, used_scripts_count)
            
            # For better browser compatibility, prefer well-supported scripts
            well_supported = [s for s in valid_scripts if s in WELL_SUPPORTED_SCRIPTS]
            if well_supported:
                valid_scripts = well_supported + [s for s in valid_scripts if s not in WELL_SUPPORTED_SCRIPTS]
            
            if not valid_scripts:
                # If no valid scripts, use any script (this shouldn't happen with 15+ scripts)
                valid_scripts = list(NUMERAL_SCRIPTS.keys())
            
            # Choose a script based on the selected sampling strategy
            if sampling_strategy == "random":
                # Completely random selection from valid scripts
                chosen_script = random.choice(valid_scripts)
            
            elif sampling_strategy == "least_used":
                # Original strategy: choose least used script (valid_scripts is already sorted by usage)
                chosen_script = valid_scripts[0]
            
            elif sampling_strategy == "weighted":
                # Weighted random selection based on script_weights
                # First filter the weights to only include valid scripts
                valid_weights = {script: script_weights.get(script, 1.0) for script in valid_scripts}
                total_weight = sum(valid_weights.values())
                if total_weight > 0:
                    # Normalize weights
                    normalized_weights = [valid_weights[script]/total_weight for script in valid_scripts]
                    chosen_script = random.choices(valid_scripts, weights=normalized_weights, k=1)[0]
                else:
                    # Fallback to random if weights are all zero
                    chosen_script = random.choice(valid_scripts)
            else:
                # Default to random if strategy not recognized
                chosen_script = random.choice(valid_scripts)
            
            # Store the script and convert the digit
            grid_scripts[row][col] = chosen_script
            grid_digits[row][col] = convert_digit(digit, chosen_script)
            
            # Update usage count
            used_scripts_count[chosen_script] += 1
    
    # Calculate script diversity statistics
    script_usage = {script: count for script, count in used_scripts_count.items() if count > 0}
    total_scripts_used = len(script_usage)
    
    return grid_digits, grid_scripts, script_usage, total_scripts_used, pi_mask

def generate_latex(grid_digits, grid_scripts, rows=10, cols=20, title="π in Indian Scripts", pi_mask=None, left_right_margin_pt=LEFT_RIGHT_MARGIN_PT):
    """
    Generate LaTeX code for the pi grid.
    """
    latex = []
    latex.append(r"\documentclass[12pt]{article}")
    latex.append(r"\usepackage[a4paper, top=2cm, left=0.18cm, right=0.18cm, bottom=0.5cm]{geometry} % Margins: top=2cm, left/right=0.18cm, bottom=0.5cm")
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
    # Calculate a fresh font size with the provided margin value
    font_size, baseline_skip = calculate_exact_font_size(rows, cols, left_right_margin_pt)
    font_size_cmd = f"\\fontsize{{{font_size:.1f}pt}}{{{baseline_skip:.1f}pt}}\\selectfont"
    print(left_right_margin_pt)
    print("I am inside", font_size_cmd)
    
    # Calculate cell scale factor for larger grids
    cell_scale = min(1.0, 30.0/max(rows, cols))  # Scale down for larger grids
    
    # Create a table for the grid
    latex.append(r"\begin{center}")
    latex.append(r"\begin{tikzpicture}")
    
    # Draw grid background with scaled size
    latex.append(r"\draw[fill=white, draw=none] (0,0) rectangle (" + 
                str(cols * cell_scale) + "," + str(rows * cell_scale) + ");")
    
    # Place digits with adjusted spacing
    for row in range(rows):
        for col in range(cols):
            # Get the digit and script
            digit_char = grid_digits[row][col]
            script = grid_scripts[row][col]
            
            # Calculate position with scaled cell size - slightly compressed spacing
            x = col * cell_scale + cell_scale/2
            y = rows * cell_scale - row * cell_scale - cell_scale/2  # Invert y-axis for LaTeX
            
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

def generate_json_data(num_digits=200, seed=None, sampling_strategy="random", script_weights=None):
    """
    Generate JSON data for the web interface based on number of digits.
    
    Parameters:
    -----------
    num_digits : int
        Number of digits of pi to display
    seed : int or None
        Random seed for reproducibility
    sampling_strategy : str
        How to choose scripts - "random", "least_used", or "weighted"
    script_weights : dict or None
        If sampling_strategy is "weighted", use these weights for each script
    """
    # Calculate optimal rows and columns for this number of digits
    rows, cols = calculate_grid_dimensions(num_digits)
    print("In generate json", seed, "strategy:", sampling_strategy)
    
    # Create the pi grid with the specified sampling strategy
    grid_digits, grid_scripts, script_usage, total_scripts_used, pi_mask = create_pi_grid(
        rows, cols, seed, sampling_strategy, script_weights
    )
    
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
        "seed": seed if seed is not None else random.randint(1, 1000000),
        "sampling_strategy": sampling_strategy
    }
    
    return json.dumps(data, indent=2)

def main():
    # Set random seed for reproducibility (or use None for random)
    seed = None
    
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

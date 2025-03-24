from flask import Flask, request, jsonify, send_file, render_template
import os
import json
import subprocess
from main import create_pi_grid, generate_latex, generate_json_data, calculate_grid_dimensions, LEFT_RIGHT_MARGIN_PT

app = Flask(__name__, static_folder=".", static_url_path="")

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/generate_pi_data', methods=['POST'])
def generate_pi_data():
    """
    Generate Pi data based on the request parameters.
    """
    data = request.json
    num_digits = data.get('num_digits', 200)
    seed = data.get('seed')
    sampling_strategy = "random"  # Always use random strategy
    script_weights = None
    
    print("In generate pi data before", seed)

    # Convert seed to integer if it's not None
    if seed is not None:
        try:
            seed = int(seed)
            print(f"Using provided seed: {seed}")
        except (ValueError, TypeError):
            # If conversion fails, leave as None for random seed
            seed = None
            print("Invalid seed format, using random seed")
    else:
        print("No seed provided, using random seed")
    print("In generate pi data", seed)

    # Generate JSON data with the random sampling strategy
    json_data = generate_json_data(
        num_digits, 
        seed, 
        sampling_strategy, 
        script_weights
    )
    
    # Parse the JSON string back to a dictionary
    result = json.loads(json_data)
    
    return jsonify(result)

@app.route('/generate_latex', methods=['POST'])
def generate_latex_endpoint():
    """
    Generate LaTeX code based on the request parameters.
    """
    data = request.json
    pi_data = data.get('data')
    title = data.get('title', 'π in Indian Scripts')
    
    if not pi_data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Extract grid data
    grid_digits = []
    grid_scripts = []
    
    # Create pi mask from highlight data
    rows = pi_data['rows']
    cols = pi_data['cols']
    pi_mask = [[False for _ in range(cols)] for _ in range(rows)]
    
    for row_idx, row_data in enumerate(pi_data['grid']):
        digit_row = []
        script_row = []
        for col_idx, cell in enumerate(row_data):
            digit_row.append(cell['digit'])
            script_row.append(cell['script'])
            # Set pi mask from highlight data
            if 'highlight' in cell:
                pi_mask[row_idx][col_idx] = cell['highlight']
        grid_digits.append(digit_row)
        grid_scripts.append(script_row)
    
    # Generate fresh LaTeX code each time to ensure we use current margin settings
    latex_code = generate_latex(grid_digits, grid_scripts, rows, cols, title, pi_mask, LEFT_RIGHT_MARGIN_PT)
    
    # Save to file
    with open('pi_visualization.tex', 'w', encoding='utf-8') as f:
        f.write(latex_code)
    
    return latex_code

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    """
    Generate PDF from LaTeX code.
    """
    data = request.json
    pi_data = data.get('data')
    title = data.get('title', 'π in Indian Scripts')
    
    if not pi_data:
        return jsonify({'error': 'No data provided'}), 400
    
    # First generate LaTeX
    grid_digits = []
    grid_scripts = []
    
    # Create pi mask from highlight data
    rows = pi_data['rows']
    cols = pi_data['cols']
    pi_mask = [[False for _ in range(cols)] for _ in range(rows)]
    
    for row_idx, row_data in enumerate(pi_data['grid']):
        digit_row = []
        script_row = []
        for col_idx, cell in enumerate(row_data):
            digit_row.append(cell['digit'])
            script_row.append(cell['script'])
            # Set pi mask from highlight data
            if 'highlight' in cell:
                pi_mask[row_idx][col_idx] = cell['highlight']
        grid_digits.append(digit_row)
        grid_scripts.append(script_row)
    
    # Generate fresh LaTeX code each time to ensure we use current margin settings
    latex_code = generate_latex(grid_digits, grid_scripts, rows, cols, title, pi_mask, LEFT_RIGHT_MARGIN_PT)
    
    # Save to file
    with open('pi_visualization.tex', 'w', encoding='utf-8') as f:
        f.write(latex_code)
    
    # Compile LaTeX to PDF
    try:
        # Run xelatex twice to ensure references are correct
        subprocess.run(['xelatex', '-interaction=nonstopmode', 'pi_visualization.tex'], check=True)
        subprocess.run(['xelatex', '-interaction=nonstopmode', 'pi_visualization.tex'], check=True)
        
        # Check if PDF was created
        if os.path.exists('pi_visualization.pdf'):
            return send_file('pi_visualization.pdf', as_attachment=True)
        else:
            return jsonify({'error': 'Failed to generate PDF'}), 500
    
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'LaTeX compilation failed: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error generating PDF: {str(e)}'}), 500

if __name__ == '__main__':
    # Generate initial data with default number of digits
    num_digits = 200
    seed = None
    sampling_strategy = 'random'  # Default to random
    print(seed, "In main")
    
    # Generate JSON data
    json_data = generate_json_data(num_digits, seed, sampling_strategy)
    
    # Save to file
    with open('pi_data.json', 'w', encoding='utf-8') as f:
        f.write(json_data)
    
    # Parse the JSON string back to a dictionary
    pi_data = json.loads(json_data)
    
    # Extract grid data
    grid_digits = []
    grid_scripts = []
    
    # Create pi mask from highlight data
    rows = pi_data['rows']
    cols = pi_data['cols']
    pi_mask = [[False for _ in range(cols)] for _ in range(rows)]
    
    for row_idx, row_data in enumerate(pi_data['grid']):
        digit_row = []
        script_row = []
        for col_idx, cell in enumerate(row_data):
            digit_row.append(cell['digit'])
            script_row.append(cell['script'])
            # Set pi mask from highlight data
            if 'highlight' in cell:
                pi_mask[row_idx][col_idx] = cell['highlight']
        grid_digits.append(digit_row)
        grid_scripts.append(script_row)
    
    # Generate fresh LaTeX code to ensure we use current margin settings
    print("I am in the server", LEFT_RIGHT_MARGIN_PT)
    latex_code = generate_latex(grid_digits, grid_scripts, rows, cols, pi_mask=pi_mask, left_right_margin_pt=LEFT_RIGHT_MARGIN_PT)
    
    # Save to file
    with open('pi_visualization.tex', 'w', encoding='utf-8') as f:
        f.write(latex_code)
    
    print("Initial data generated. Starting server...")
    app.run(debug=True) 
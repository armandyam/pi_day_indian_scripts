# Pi Day Visualization - Indian Scripts

A beautiful visualization tool for π (pi) day that displays the digits of π using multiple Indian scripts in a grid format. The visualization features:

- Random selection of Indian scripts for each digit
- The first digit (3) displayed in Latin to make it recognizable
- A π symbol shape highlighted in red within the grid
- LaTeX output for high-quality PDF generation
- Interactive web interface to customize the visualization

## Requirements

### For the web interface
- Python 3.7+
- Flask
- Required fonts (see below)

### For PDF generation
- XeLaTeX with the following packages:
  - fontspec
  - xcolor
  - tikz
  - multicol
  - lmodern
- Noto Sans fonts for various Indian scripts (see below)

## Setup

1. Clone this repository:
```
git clone https://github.com/armandyam/pi_day_indian_scripts.git
cd pi_day_indian_scripts
```

2. Create a virtual environment and install dependencies:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Download the required fonts from Google Noto Fonts and place them in the `fonts` directory:
```
mkdir -p fonts
# Download Noto fonts into the fonts directory
```

You can download Noto fonts from: https://notofonts.github.io/

Required fonts:
- texgyrepagella-regular.otf (for Latin)
- NotoSansDevanagari-Regular.ttf
- NotoSansBengali-Regular.ttf
- NotoSansGujarati-Regular.ttf
- NotoSansGurmukhi-Regular.ttf
- NotoSansKannada-Regular.ttf
- NotoSansMalayalam-Regular.ttf
- NotoSansTamil-Regular.ttf
- NotoSansTelugu-Regular.ttf
- NotoSansOriya-Regular.ttf
- NotoSansArabic-Regular.ttf
- NotoSansMeeteiMayek-Regular.ttf
- NotoSansOlChiki-Regular.ttf

## Running the Application

### Web Interface

Start the Flask server:
```
python server.py
```

Then open your browser and navigate to: http://localhost:5000

### Command Line

You can also generate the visualization directly from the command line:
```
python main.py
```

This will:
1. Generate a Pi visualization with default settings (200 digits)
2. Create a LaTeX file (`pi_visualization.tex`)
3. Create a JSON data file (`pi_data.json`)
4. Give you the option to compile the LaTeX to PDF

## Customization

Through the web interface, you can customize:
- The number of digits to display
- The random seed for reproducibility
- The title of the visualization

## How It Works

The program:
1. Calculates the optimal grid dimensions based on the A4 paper ratio
2. Randomly assigns each digit of π to one of the Indian scripts
3. Creates a π symbol shape within the grid for highlighting
4. Ensures the first digit (3) is always displayed in Latin
5. Generates the visualization as a LaTeX document
6. Compiles the LaTeX to PDF using XeLaTeX (if requested)

## Credits

- The digits of π are displayed in 15+ different Indian scripts
- Fonts are from the Google Noto Sans project

## License

MIT License 

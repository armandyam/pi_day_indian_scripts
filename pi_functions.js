// Unicode numeral scripts with starting code points for digits (0-9)
const NUMERAL_SCRIPTS = {
    "Assamese": 0x09E6,
    "Bengali": 0x09E6,
    "Devanagari": 0x0966,
    "Gujarati": 0x0AE6,
    "Gurmukhi": 0x0A66,
    "Kannada": 0x0CE6,
    "Malayalam": 0x0D66,
    "Odia": 0x0B66,
    "Ol Chiki": 0x1C50,
    "Tamil": 0x0BE6,
    "Telugu": 0x0C66,
    "Urdu": 0x06F0,
    "Kashmiri": 0x06F0,
    "Sindhi": 0x06F0,
    "Manipuri": 0xABF0,
    "Latin": 0x0030
};

// Well-supported scripts in LaTeX and browsers
const WELL_SUPPORTED_SCRIPTS = [
    "Latin", "Devanagari", "Bengali", "Assamese", "Gujarati", 
    "Gurmukhi", "Tamil", "Telugu", "Kannada", "Malayalam", 
    "Odia", "Urdu", "Kashmiri", "Sindhi", "Manipuri", "Ol Chiki"
];

// Constants for grid configuration and constraints
const MIN_DIGITS = 10;
const MAX_DIGITS = 430;
const A4_RATIO = 1.414; // A4 page ratio (height/width)

// A4 paper dimensions in points
const A4_WIDTH_PT = 597.0;  // 21 cm or 210 mm
const A4_HEIGHT_PT = 842.0; // 29.7 cm or 297 mm

// Layout parameters
const TOP_MARGIN_PT = 56.9;  
const BOTTOM_MARGIN_PT = 14.2;  
const LEFT_RIGHT_MARGIN_PT = 5.0;  
const TITLE_SPACE_PT = 42.0;  
const FOOTER_SPACE_PT = 20.0;  

function calculateGridDimensions(numDigits) {
    /**
     * Calculate optimal rows and columns for a given number of digits to fit an A4 page ratio.
     */
    // Ensure numDigits is within the acceptable range
    numDigits = Math.max(MIN_DIGITS, Math.min(MAX_DIGITS, numDigits));

    // Calculate the actual available space dimensions after accounting for margins
    const availableWidth = A4_WIDTH_PT - (2 * LEFT_RIGHT_MARGIN_PT);
    const availableHeight = A4_HEIGHT_PT - TOP_MARGIN_PT - BOTTOM_MARGIN_PT - TITLE_SPACE_PT - FOOTER_SPACE_PT;

    // Calculate the actual ratio based on available space
    const actualRatio = availableHeight / availableWidth;

    // Calculate optimal dimensions to match the actual available space ratio (portrait orientation)
    let cols = Math.sqrt(numDigits / actualRatio);
    let rows = numDigits / cols;

    // Round to whole numbers, ensuring we have enough cells for the digits
    cols = Math.max(3, Math.round(cols)); // Minimum 3 columns
    rows = Math.max(3, Math.ceil(numDigits / cols)); // Minimum 3 rows, round up to ensure enough cells

    console.log(`Available space ratio: ${actualRatio.toFixed(3)} (vs A4 ratio: ${A4_RATIO.toFixed(3)})`);
    console.log(`Grid dimensions: ${rows} rows x ${cols} columns`);
    
    return { rows, cols };
}

// Example usage
console.log(calculateGridDimensions(250));

function calculateExactFontSize(rows, cols, leftRightMarginPt = LEFT_RIGHT_MARGIN_PT) {
    /**
     * Calculate precise font size in points to fit digits optimally on an A4 page.
     * Returns an object containing fontSize and baselineSkip values for LaTeX.
     */
    
    // Calculate available space on the page
    const availableWidth = A4_WIDTH_PT - (2 * leftRightMarginPt);
    const availableHeight = A4_HEIGHT_PT - TOP_MARGIN_PT - BOTTOM_MARGIN_PT - TITLE_SPACE_PT - FOOTER_SPACE_PT;

    // Calculate cell dimensions with scaling for larger grids
    const cellScale = Math.min(1.0, 30.0 / Math.max(rows, cols)); // Scale down for larger grids

    const cellWidth = availableWidth / cols;
    const cellHeight = availableHeight / rows;

    // Use the smaller dimension to ensure cells remain square-ish
    // Increase the percentage for larger grids to reduce whitespace
    const cellSize = Math.min(cellWidth, cellHeight);
    const fontPercentage = Math.min(0.9, 0.7 + 0.2 * (1 - cellScale)); // Larger font percentage to reduce whitespace
    const fontSize = cellSize * fontPercentage;

    // Reduced baseline skip to decrease vertical spacing
    const baselineSkip = fontSize * 1.05; // Reduced from 1.2 to 1.05

    console.log(fontSize, baselineSkip, leftRightMarginPt, cols, rows, cellScale);
    
    return { fontSize, baselineSkip };
}

// Example usage
console.log(calculateExactFontSize(30, 20));


// Import a high-precision library for handling pi (use decimal.js or a similar library)
// const Decimal = require('decimal.js');

// Set precision for Decimal.js (1000 digits)
Decimal.set({ precision: 1000 });

function getPiDigits(n = 200) {
    let pi = new Decimal(0); 

    // Compute Pi using Decimal.js with Chudnovsky Algorithm
    pi = pi.acos(-1); // ✅ This computes high-precision π
    let piStr = pi.toFixed(n); // Convert to a string with `n` digits

    return piStr.slice(0, n + 1); // Return π including decimal point
}

function convertDigit(digit, script) {
    /**
     * Convert a single digit to the specified script.
     */
    if (digit === '.') {
        // Return the decimal point as is
        return '.';
    }

    const startCode = NUMERAL_SCRIPTS[script];
    return String.fromCharCode(startCode + parseInt(digit));
}

// Example usage
console.log(getPiDigits(200));
console.log(convertDigit('5', 'Devanagari'));


function generatePiShapeMask(rows, cols) {
    /**
     * Generate a mask in the shape of the π symbol.
     * Returns a 2D array where true indicates a pixel that should be colored.
     */

    // Create a blank 2D array filled with false
    let mask = Array.from({ length: rows }, () => Array(cols).fill(false));

    // Calculate dimensions for the pi symbol
    const width = cols * 0.7;
    const height = rows * 0.7;
    const xOffset = (cols - width) / 2;
    const yOffset = (rows - height) / 2;

    // Define the horizontal line of pi
    const lineHeight = height * 0.2;
    for (let x = Math.floor(xOffset); x < Math.floor(xOffset + width); x++) {
        for (let y = Math.floor(yOffset); y < Math.floor(yOffset + lineHeight); y++) {
            if (x >= 0 && x < cols && y >= 0 && y < rows) {
                mask[y][x] = true;
            }
        }
    }

    // Define the left vertical line
    const leftX = xOffset + width * 0.25;
    for (let x = Math.floor(leftX - width * 0.1); x < Math.floor(leftX + width * 0.1); x++) {
        for (let y = Math.floor(yOffset); y < Math.floor(yOffset + height); y++) {
            if (x >= 0 && x < cols && y >= 0 && y < rows) {
                mask[y][x] = true;
            }
        }
    }

    // Define the right vertical line
    const rightX = xOffset + width * 0.75;
    for (let x = Math.floor(rightX - width * 0.1); x < Math.floor(rightX + width * 0.1); x++) {
        for (let y = Math.floor(yOffset); y < Math.floor(yOffset + height); y++) {
            if (x >= 0 && x < cols && y >= 0 && y < rows) {
                mask[y][x] = true;
            }
        }
    }

    return mask;
}

// Example usage
console.log(generatePiShapeMask(30, 50));


function getValidScripts(row, col, gridScripts, rows, cols, usedScriptsCount) {
    /**
     * Get a list of valid scripts that don't conflict with adjacent cells,
     * prioritizing scripts that have been used less frequently.
     */
    
    let adjacentScripts = new Set();

    // Check all 8 adjacent positions
    for (let dr of [-1, 0, 1]) {
        for (let dc of [-1, 0, 1]) {
            if (dr === 0 && dc === 0) continue; // Skip the current cell

            let r = row + dr;
            let c = col + dc;

            if (r >= 0 && r < rows && c >= 0 && c < cols && gridScripts[r][c] !== null) {
                adjacentScripts.add(gridScripts[r][c]);
            }
        }
    }

    // Get scripts that aren't used in adjacent cells
    let validScripts = Object.keys(NUMERAL_SCRIPTS).filter(script => !adjacentScripts.has(script));

    // Sort by usage count (prefer less used scripts)
    validScripts.sort((a, b) => (usedScriptsCount[a] || 0) - (usedScriptsCount[b] || 0));

    return validScripts;
}

// // Example usage:
// let gridScripts = Array.from({ length: 5 }, () => Array(5).fill(null));
// let usedScriptsCount = { "Devanagari": 3, "Bengali": 2, "Tamil": 1 };

// console.log(getValidScripts(2, 2, gridScripts, 5, 5, usedScriptsCount));


function createPiGrid(rows = 10, cols = 20, seed = null, samplingStrategy = "random", scriptWeights = null) {
    /**
     * Create a grid of pi digits using different scripts for adjacent cells.
     * 
     * Parameters:
     * rows, cols : int - Dimensions of the grid
     * seed : int or null - Random seed for reproducibility
     * samplingStrategy : str - "random", "least_used", or "weighted"
     * scriptWeights : object or null - If "weighted", use these weights for each script
     */
    
    // Set a random seed for reproducibility
    let seedInt;
    if (seed !== null) {
        seedInt = parseInt(seed);
        if (isNaN(seedInt)) {
            seedInt = Math.floor(Math.random() * 1000000);
            console.log(`Invalid seed provided, using random seed: ${seedInt}`);
        }
    } else {
        seedInt = Math.floor(Math.random() * 1000000);
        console.log(`No seed provided, using random seed: ${seedInt}`);
    }
    Math.seedrandom(seedInt); // Requires seedrandom library

    const piDigits = getPiDigits(rows * cols);

    // Initialize grid for scripts and digits
    let gridScripts = Array.from({ length: rows }, () => Array(cols).fill(null));
    let gridDigits = Array.from({ length: rows }, () => Array(cols).fill(null));

    // Generate pi shape mask for colored cells
    let piMask = generatePiShapeMask(rows, cols);
    console.log("Pi Mask:", piMask); // ✅ Check if `piMask` is being created correctly

    // Track script usage
    let usedScriptsCount = {};
    Object.keys(NUMERAL_SCRIPTS).forEach(script => usedScriptsCount[script] = 0);

    // Set first digit to Latin "3"
    gridScripts[0][0] = "Latin";
    gridDigits[0][0] = "3";
    usedScriptsCount["Latin"] += 1;

    // Set second position to decimal point
    gridScripts[0][1] = "Latin";
    gridDigits[0][1] = ".";
    usedScriptsCount["Latin"] += 1;

    // Default weights for weighted sampling if none provided
    if (scriptWeights === null) {
        scriptWeights = {};
        Object.keys(NUMERAL_SCRIPTS).forEach(script => scriptWeights[script] = 1.0);
    }

    // Fill the rest of the grid
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            // Skip first two positions (already filled)
            if ((row === 0 && col === 0) || (row === 0 && col === 1)) continue;

            let index = row * cols + col;
            let digit = index < piDigits.length ? piDigits[index] : "0"; // Use "0" if out of digits

            // Skip if it's a decimal point (already handled)
            if (digit === ".") continue;

            // Get valid scripts for this position
            let validScripts = getValidScripts(row, col, gridScripts, rows, cols, usedScriptsCount);

            // Prioritize well-supported scripts
            let wellSupported = validScripts.filter(s => WELL_SUPPORTED_SCRIPTS.includes(s));
            if (wellSupported.length > 0) {
                validScripts = wellSupported.concat(validScripts.filter(s => !WELL_SUPPORTED_SCRIPTS.includes(s)));
            }

            if (validScripts.length === 0) {
                // Fallback to any script (shouldn't happen)
                validScripts = Object.keys(NUMERAL_SCRIPTS);
            }

            let chosenScript;
            if (samplingStrategy === "random") {
                chosenScript = validScripts[Math.floor(Math.random() * validScripts.length)];
            } else if (samplingStrategy === "least_used") {
                validScripts.sort((a, b) => (usedScriptsCount[a] || 0) - (usedScriptsCount[b] || 0));
                chosenScript = validScripts[0];
            } else if (samplingStrategy === "weighted") {
                // Weighted random selection
                let validWeights = validScripts.map(script => scriptWeights[script] || 1.0);
                let totalWeight = validWeights.reduce((sum, w) => sum + w, 0);
                
                if (totalWeight > 0) {
                    let cumulativeWeights = [];
                    let sum = 0;
                    validWeights.forEach(w => {
                        sum += w;
                        cumulativeWeights.push(sum / totalWeight);
                    });

                    let rand = Math.random();
                    for (let i = 0; i < cumulativeWeights.length; i++) {
                        if (rand < cumulativeWeights[i]) {
                            chosenScript = validScripts[i];
                            break;
                        }
                    }
                } else {
                    chosenScript = validScripts[Math.floor(Math.random() * validScripts.length)];
                }
            } else {
                chosenScript = validScripts[Math.floor(Math.random() * validScripts.length)];
            }

            // Store script and converted digit
            gridScripts[row][col] = chosenScript;
            gridDigits[row][col] = convertDigit(digit, chosenScript);

            // Update usage count
            usedScriptsCount[chosenScript] += 1;
        }
    }

    // Calculate script diversity statistics
    let scriptUsage = Object.fromEntries(Object.entries(usedScriptsCount).filter(([_, count]) => count > 0));
    let totalScriptsUsed = Object.keys(scriptUsage).length;

    return { gridDigits, gridScripts, scriptUsage, totalScriptsUsed, piMask };
}

// Example usage:
console.log(createPiGrid(10, 20));



function generateLatex(gridDigits, gridScripts, rows = 10, cols = 20, title = "π in Indian Scripts", piMask = null, leftRightMarginPt = LEFT_RIGHT_MARGIN_PT) {
    /**
     * Generate LaTeX code for the pi grid.
     */

    let latex = [];

    latex.push("\\documentclass[12pt]{article}");
    latex.push("\\usepackage[a4paper, top=2cm, left=0.18cm, right=0.18cm, bottom=0.5cm]{geometry}");
    latex.push("\\usepackage{fontspec}");
    latex.push("\\usepackage{xcolor}");
    latex.push("\\usepackage{tikz}");
    latex.push("\\usepackage{array}");
    latex.push("\\usepackage{colortbl}");
    latex.push("\\usepackage{multicol}");
    latex.push("\\usepackage{fancyhdr}");
    latex.push("\\usepackage{graphicx}");
    latex.push("\\usepackage{lmodern}");

    // Set up fonts
    latex.push("\\setmainfont{Noto Sans}");

    // Define colors
    latex.push("\\definecolor{bg}{RGB}{252, 252, 252}");
    latex.push("\\definecolor{gridline}{RGB}{220, 220, 220}");
    latex.push("\\definecolor{title}{RGB}{50, 50, 50}");
    latex.push("\\definecolor{highlight}{RGB}{231, 76, 60}");

    // Page setup
    latex.push("\\pagestyle{fancy}");
    latex.push("\\fancyhf{}");
    latex.push("\\renewcommand{\\headrulewidth}{0pt}");
    latex.push("\\renewcommand{\\footrulewidth}{0pt}");
    latex.push("\\fancyfoot[C]{\\thepage}");

    // Background color
    latex.push("\\pagecolor{bg}");
    latex.push("\\pagecolor{white}");

    // Begin document
    latex.push("\\begin{document}");
    latex.push("\\thispagestyle{empty}");

    // Title
    latex.push("\\begin{center}");
    latex.push(`{\\Huge\\textbf{${title}}}`);
    latex.push("\\vspace{0.5cm}");
    latex.push("\\end{center}");

    // Calculate font size
    let { fontSize, baselineSkip } = calculateExactFontSize(rows, cols, leftRightMarginPt);
    let fontSizeCmd = `\\fontsize{${fontSize.toFixed(1)}pt}{${baselineSkip.toFixed(1)}pt}\\selectfont`;

    // Calculate cell scale factor for larger grids
    let cellScale = Math.min(1.0, 30.0 / Math.max(rows, cols));

    // Create a table for the grid
    latex.push("\\begin{center}");
    latex.push("\\begin{tikzpicture}");

    // Draw grid background with scaled size
    latex.push(`\\draw[fill=white, draw=none] (0,0) rectangle (${(cols * cellScale).toFixed(2)},${(rows * cellScale).toFixed(2)});`);

    // Place digits with adjusted spacing
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            let digitChar = gridDigits[row][col];
            let script = gridScripts[row][col];

            let x = (col * cellScale + cellScale / 2).toFixed(2);
            let y = (rows * cellScale - row * cellScale - cellScale / 2).toFixed(2); // Invert y-axis for LaTeX

            let colorCmd = (piMask && piMask[row][col]) ? "\\textcolor{highlight}" : "";

            // Determine correct font
            let fontName;
            if (["Urdu", "Kashmiri", "Sindhi"].includes(script)) {
                fontName = "Noto Sans Arabic";
            } else if (script === "Assamese") {
                fontName = "Noto Sans Bengali";
            } else if (script === "Manipuri") {
                fontName = "Noto Sans Meetei Mayek";
            } else if (script === "Odia") {
                fontName = "Noto Sans Oriya";
            } else if (script === "Latin") {
                fontName = "Noto Sans";
            } else {
                fontName = `Noto Sans ${script}`;
            }

            // Add digit node to LaTeX
            if (script === "Latin" && digitChar === ".") {
                latex.push(`\\node at (${x},${y}) {${colorCmd}{${fontSizeCmd} .}};`);
            } else {
                latex.push(`\\node at (${x},${y}) {${colorCmd}{\\fontspec{${fontName}}${fontSizeCmd} ${digitChar}}};`);
            }
        }
    }

    latex.push("\\end{tikzpicture}");
    latex.push("\\end{center}");

    // Add legend for scripts
    latex.push("\\vspace{1cm}");

    // Get unique scripts used
    let usedScripts = new Set();
    gridScripts.forEach(row => row.forEach(script => {
        if (script) usedScripts.add(script);
    }));

    let sortedScripts = Array.from(usedScripts).sort();

    // Add footer with information
    latex.push("\\vfill");
    latex.push("\\begin{center}");
    latex.push(`\\tiny{This poster displays the first ${rows * cols} digits of π using ${sortedScripts.length} different Indian numeral scripts.}`);
    latex.push("\\end{center}");

    // End document
    latex.push("\\end{document}");

    return latex.join("\n");
}

// Example usage:
let gridDigits = [
    ["3", ".", "1", "4", "1"],
    ["5", "9", "2", "6", "5"],
    ["3", "5", "8", "9", "7"]
];

let gridScripts = [
    ["Latin", "Latin", "Devanagari", "Tamil", "Gujarati"],
    ["Odia", "Bengali", "Gurmukhi", "Telugu", "Kannada"],
    ["Malayalam", "Manipuri", "Urdu", "Sindhi", "Kashmiri"]
];

console.log(generateLatex(gridDigits, gridScripts, 3, 5));

function generateJsonData(numDigits = 200, seed = null, samplingStrategy = "random", scriptWeights = null) {
    /**
     * Generate JSON data for the web interface based on number of digits.
     *
     * Parameters:
     * numDigits : int - Number of digits of pi to display
     * seed : int or null - Random seed for reproducibility
     * samplingStrategy : str - "random", "least_used", or "weighted"
     * scriptWeights : object or null - If "weighted", use these weights for each script
     */

    // Calculate optimal rows and columns for this number of digits
    let { rows, cols } = calculateGridDimensions(numDigits);
    console.log("In generate JSON", seed, "strategy:", samplingStrategy);

    // Create the pi grid with the specified sampling strategy
    let { gridDigits, gridScripts, scriptUsage, totalScriptsUsed, piMask } = createPiGrid(
        rows, cols, seed, samplingStrategy, scriptWeights
    );

    // Convert grid data to format suitable for JSON
    let gridData = [];
    for (let row = 0; row < rows; row++) {
        let rowData = [];
        for (let col = 0; col < cols; col++) {
            let digit = gridDigits[row][col];
            let script = gridScripts[row][col];
            let unicode = (digit !== ".") ? `0x${digit.charCodeAt(0).toString(16).toUpperCase()}` : "0x2E";
            let highlight = piMask[row][col] ? true : false;

            rowData.push({ digit, script, unicode, highlight });
        }
        gridData.push(rowData);
    }

    // Create JSON object
    let data = {
        "grid": gridData,
        "script_usage": scriptUsage,
        "total_scripts_used": totalScriptsUsed,
        "rows": rows,
        "cols": cols,
        "num_digits": numDigits,
        "seed": seed !== null ? seed : Math.floor(Math.random() * 1000000),
        "sampling_strategy": samplingStrategy,
        "pi_mask": piMask // ✅ Now it's included
    };


    return JSON.stringify(data, null, 2);
}

// Example usage:
console.log(generateJsonData(200));

function convertToLatin(digit, script) {
    if (digit === ".") return ".";  // Keep decimal points unchanged

    // Use NUMERAL_SCRIPTS to get the base Unicode point
    let startCode = NUMERAL_SCRIPTS[script];
    if (!startCode) return digit; // Return the original if the script is unknown

    let latinEquivalent = (digit.charCodeAt(0) - startCode).toString();
    return latinEquivalent;
}


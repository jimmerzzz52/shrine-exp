const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const inputDir = path.join(__dirname, 'img');
const outputDir = path.join(__dirname, 'optimized-img');

// Create output directory if it doesn't exist
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
}

// Function to optimize images
const optimizeImages = async () => {
    const files = fs.readdirSync(inputDir);
    
    for (const file of files) {
        const inputFile = path.join(inputDir, file);
        const outputFile = path.join(outputDir, file);

        try {
            await sharp(inputFile)
                .resize(800) // Resize image to 800px width
                .jpeg({ quality: 80 }) // Compress image to 80% quality
                .toFile(outputFile);

            console.log(`Optimized ${file}`);
        } catch (error) {
            console.error(`Error optimizing ${file}:`, error);
        }
    }
};

optimizeImages();

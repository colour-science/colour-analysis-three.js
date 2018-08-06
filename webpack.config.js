const path = require('path');

module.exports = {
    entry: './src/index.js',
    output: {
        library: 'ColourAnalysis',
        filename: 'colour-analysis.js',
        path: path.resolve(__dirname, 'dist')
    }
};

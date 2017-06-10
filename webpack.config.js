const path = require('path');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const styleScss = new ExtractTextPlugin('[name].style.css');

function getPath(myPath) { return path.resolve(path.join(__dirname, myPath)); }

const config = {
    context: getPath('./frontend'),
    entry: {
        main: [ getPath('./frontend/js/main.js'), getPath('./scss/main/index.scss') ],
    },
    output: {
        path: getPath('./server/static'),
        filename: '[name].js',
    },
    resolve: {
        extensions: [ '*', '.js', '.jsx', '.scss' ],
    },
    module: {
        rules: [{
            test: /\.(js|jsx)$/,
            include: getPath('./frontend/js'),
            exclude: /node_modules/,
            use: [{
                loader: 'babel-loader',
                options: {
                    presets: [
                        [ 'es2015', { modules: false } ],
                        [ 'react' ],
                    ],
                },
            }],
        }, {
            test: /\.scss$/,
            use: styleScss.extract({
                use: [ 'css-loader', 'sass-loader' ],
            }),
        }],
    },
    plugins: [
        styleScss,
    ],
};

module.exports = config;

const webpack = require('webpack');
const path = require('path');

function getPath(myPath) { return path.resolve(path.join(__dirname, myPath)); }

const config = {
    context: getPath('./frontend'),
    entry: getPath('./frontend/js/app.js'),
    output: {
        path: getPath('./server/static'),
        filename: 'build.js',
    },
    module: {
        rules: [{
            test: /\.js$/,
            include: getPath('./frontend/js'),
            exclude: /node_modules/,
            use: [{
                loader: 'babel-loader',
                options: {
                    presets: [
                        ['es2015', { modules: false }],
                    ],
                },
            }],
        }],
    },
};

module.exports = config;

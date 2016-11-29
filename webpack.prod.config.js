var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var config = require('./webpack.base.config.js');

 
config[0].plugins = config[0].plugins.concat([
    new BundleTracker({filename: './webpack-stats-prod.json'}),
    new webpack.DefinePlugin({
        'process.env': {
            'NODE_ENV': JSON.stringify('production')
        }
    }),
    new webpack.optimize.OccurenceOrderPlugin(),
    new webpack.optimize.UglifyJsPlugin({
        compressor: {
            warnings: false
        }
    })
]);

config[0].output.path = path.resolve('./assets/dist');

module.exports = config;

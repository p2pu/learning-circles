var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

var config = require('./webpack.base.config.js');

config[0].plugins = config[0].plugins.concat([
    new BundleTracker({filename: './assets/frontend-webpack-manifest-dev.json'}),
]);

config[1].devtool = 'inline-source-map';
config[1].plugins = config[1].plugins.concat([
    new BundleTracker({filename: './assets/style-webpack-manifest-dev.json'}),
]);


module.exports = config;

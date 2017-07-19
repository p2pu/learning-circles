var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

var config = require('./webpack.base.config.js');

config[0].plugins = config[0].plugins.concat([
    new BundleTracker({filename: './webpack-stats.json'}),
]);

config[1].devtool = 'inline-source-map';

module.exports = config;

const config = require('./webpack.config');

const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

config[0].plugins = config[0].plugins.concat([new BundleAnalyzerPlugin()]);

module.exports = config;

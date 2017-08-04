var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var config = require('./webpack.base.config.js');


config[0].plugins = config[0].plugins.concat([
  new webpack.LoaderOptionsPlugin({
    minimize: true,
    debug: false
  }),
  new BundleTracker({filename: './assets/frontend-webpack-manifest.json'}),
  new webpack.DefinePlugin({
    'process.env': {
      'NODE_ENV': JSON.stringify('production')
    }
  }),
  new webpack.optimize.UglifyJsPlugin({
    beautify: false,
    mangle: {
      screw_ie8: true,
      keep_fnames: true
    },
    compress: {
      screw_ie8: true
    },
    comments: false,
    compressor: {
      warnings: false
    }
  })
]);
config[0].output.path = path.resolve('./assets/dist');

config[1].plugins = config[1].plugins.concat([
  new BundleTracker({filename: './assets/style-webpack-manifest.json'}),
  new webpack.optimize.UglifyJsPlugin({
    compressor: {
      warnings: false
    }
  })
]);
config[1].output.path = path.resolve('./assets/dist');

module.exports = config;

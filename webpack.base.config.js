var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var fs = require("fs");

function getReactChunks(){
  // Add all jsx files in /assets/js as entries
  var files = fs.readdirSync('./assets/js/').filter(function(f){
    return f.endsWith('.jsx');
  })

  var entries = {};
  files.forEach(function(f){
    entries[f.replace(/.jsx/, '')] = './assets/js/' + f;
  });
  return entries;
}

const reactBuild = {
  name: 'react',
  context: __dirname,
  entry: getReactChunks(),
  output: {
    path: path.resolve('./assets/bundles/'),
    filename: "[name]-[hash].js",
  },
  module: {
    loaders: [
      { 
        test: /\.scss$/, 
        loaders: ['style-loader', 'css-loader', 'sass-loader']
      },
      { 
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader?presets[]=es2015&presets[]=react'
      },
    ],
  },
  plugins: [],
  resolve: {
    modulesDirectories: ['node_modules', 'bower_components'],
    extensions: ['', '.js', '.jsx', '.scss']
  },
};

const styleBuild = {
  name: 'css',
  entry: {
    sass: './static/sass/p2pu-custom.scss'
  },
  module: {
    loaders: [
      {
        test: /\.woff2?$|\.ttf$|\.eot$|\.svg$|\.png$/,
        loader: 'file-loader?outputPath=dist/',
      },
      { 
        test: /\.scss$/,
        loader: ExtractTextPlugin.extract('style-loader', 'css-loader!sass-loader')
      },
    ]
  },
  sassLoader: {
    includePaths: [path.resolve("./static/")]
  },
  output: {
    path: path.resolve('./static/css/'),
    filename: "[name].css.js",
  },
  plugins: [
    new ExtractTextPlugin("build.styles.css")
  ]
}

module.exports = [reactBuild, styleBuild]

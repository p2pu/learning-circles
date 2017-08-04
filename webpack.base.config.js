var path = require("path");
var webpack = require('webpack');
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var fs = require("fs");

function getReactChunks(){
  // Add all jsx files in /assets/js as entries
  var files = fs.readdirSync('./frontend/').filter(function(f){
    return f.endsWith('.jsx');
  })

  var entries = {};
  files.forEach(function(f){
    entries[f.replace(/.jsx/, '')] = './frontend/' + f;
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
    rules: [
      { 
        test: /\.scss$/,
        use: [
          { loader: 'style-loader'},
          { loader: 'css-loader'},
          { loader: 'sass-loader'}
        ]
      },
      { 
        test: /\.css$/,
        use: [
          { loader: 'style-loader'},
          { loader: 'css-loader'}
        ]
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
    modules: [
      path.join(__dirname, "assets/js"),
      'node_modules',
    ],
    extensions: ['.js', '.jsx', '.scss']
  },
};

const styleBuild = {
  name: 'css',
  entry: {
    'p2pu-strap': './static/sass/p2pu-custom.scss'
  },
  module: {
    rules: [
      {
        test: /\.woff2?$|\.ttf$|\.eot$|\.svg$|\.png$/,
        use: [
          {
            loader: 'file-loader',
          }
        ]
      },
      { 
        test: /\.scss$/,
        use: ExtractTextPlugin.extract({
          fallback: 'style-loader',
          use: [{
            loader: 'css-loader',
            options: {
              sourceMap: true,
            },
          }, {
            loader: 'sass-loader',
            options: {
              sourceMap: true,
              includePaths: [path.resolve("./static/")]
            }
          }]
        }),
      },
    ]
  },
  output: {
    path: path.resolve('./assets/bundles/'),
    filename: "[name].[hash].js",
  },
  plugins: [
    new ExtractTextPlugin("[name].[hash].css")
  ]
}

module.exports = [reactBuild, styleBuild]

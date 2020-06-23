var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CompressionPlugin = require('compression-webpack-plugin');


var fs = require("fs");

function getReactChunks(){
  // Add all jsx files in /assets/js as entries
  var files = fs.readdirSync('./frontend/').filter(function(f){
    return f.endsWith('.jsx');
  })

  var entries = {};
  files.forEach(function(f){
    entries[f.replace(/.jsx/, '')] = ['babel-polyfill', './frontend/' + f];
  });
  return entries;
}

const reactBuild = {
  name: 'react',
  context: __dirname,
  entry: getReactChunks(),
  output: {
    path: path.resolve('./assets/dist/'),
    filename: "[name]-[hash].js",
  },
  devtool: 'source-map',
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
        loader: 'babel-loader'
      },
    ],
  },
  externals: {
    jquery: 'jQuery',
    $: 'jQuery'
  },
  optimization: {
    //runtimeChunk: "single", // enable "runtime" chunk
    splitChunks: {
      cacheGroups: {
        common: {
          name: 'common',
          chunks: 'initial',
          minChunks: 3
        }
      }
    }
  },
  plugins: [
    new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
    new BundleTracker({filename: './assets/frontend-webpack-manifest.json'}),
    new CompressionPlugin()
  ],
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
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
            options: {
              sourceMap: true,
            },
          },
          {
            loader: 'sass-loader',
            options: {
              sourceMap: true,
              includePaths: [path.resolve("./static/"), path.resolve("./node_modules/")]
            }
          }
        ]
      },
    ]
  },
  output: {
    path: path.resolve('./assets/dist/'),
    filename: "[name].[hash].js",
  },
  plugins: [
    new MiniCssExtractPlugin({filename: "[name].[hash].css"}),
    new BundleTracker({filename: './assets/style-webpack-manifest.json'}),
  ],
}

module.exports = [reactBuild, styleBuild]

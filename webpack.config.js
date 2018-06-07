var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

var fs = require("fs");
var env = process.env.NODE_ENV;

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
    path: path.resolve('./assets/dist/'),
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
        loader: 'babel-loader?presets[]=env&presets[]=react&presets[]=stage-2'
      },
    ],
  },
  plugins: [
    new BundleTracker({filename: './assets/frontend-webpack-manifest.json'}),
    new webpack.DefinePlugin({
       'process.env.NODE_ENV': JSON.stringify(env)
    }),
    new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery"
    }),
    new webpack.optimize.CommonsChunkPlugin({
      name: 'common',
    }),
    new webpack.optimize.OccurrenceOrderPlugin(true),
    new webpack.optimize.UglifyJsPlugin(),
    new webpack.optimize.AggressiveMergingPlugin(),
    new BundleAnalyzerPlugin(),
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
    path: path.resolve('./assets/dist/'),
    filename: "[name].[hash].js",
  },
  plugins: [
    new ExtractTextPlugin("[name].[hash].css"),
    new BundleTracker({filename: './assets/style-webpack-manifest.json'}),
  ]
}

module.exports = [reactBuild, styleBuild]

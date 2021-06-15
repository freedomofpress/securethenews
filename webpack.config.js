var webpack       = require('webpack');
const { merge }   = require('webpack-merge');
var autoprefixer  = require('autoprefixer');
var BundleTracker = require('webpack-bundle-tracker');
var MiniCssExtractPlugin = require('mini-css-extract-plugin');
var path = require('path');

var TARGET = process.env.npm_lifecycle_event;
process.env.BABEL_ENV = TARGET;

var target = __dirname + '/client/build';

var STATIC_URL = process.env.STATIC_URL || '/static/';
var sassData = '$static-url: "' + STATIC_URL + '";';
console.log('Using STATIC_URL', STATIC_URL);


var common = {
	entry: {
		build: __dirname + '/client/src/index.js',
	},

	output: {
		path: target,
		filename: '[name].js'
	},

	resolve: {
		alias: {
			'~': __dirname + '/client/src',
		},
		extensions: ['.js', '.jsx'],
		modules: ['node_modules']
	},

	module: {
		rules: [
			{
				test: /\.jsx?$/,
				use: [
					{
						loader: 'babel-loader',
						options: {
							presets: [
								'@babel/preset-react',
								// Setting `modules` false, prevents babel from trying to use
								// commonjs imports, which messes up our nice clean ES6 imports
								// provided directly by Webpack:
								// https://github.com/webpack/webpack/issues/4961#issuecomment-304938963
								['@babel/preset-env', { modules: false }]
							],
						},
					}
				]
			},
			{
				test: /\.s[ca]ss$/,
				use: [
					MiniCssExtractPlugin.loader,
					'css-loader',
					'postcss-loader',
					{
						loader: 'sass-loader',
						options: {
							includePaths: [path.resolve(__dirname, 'node_modules/')],
							data: sassData
						}
					}
				],
			},
			{
				test: /\.css$/,
				use: [MiniCssExtractPlugin.loader, 'css-loader', 'postcss-loader']
			},
			{
				test: /\.(jade|pug)$/,
				use: ['pug-loader']
			},
			{
				test: /\.(woff2?|ttf|eot|svg|otf)(\?v=\d+\.\d+\.\d+)?$/,
				use: [{
					loader: 'file-loader',
					options: {
						name: '[name].[ext]',
						outputPath: 'fonts/'
					}
				}]
			}
		]
	},

	plugins: [
		new MiniCssExtractPlugin({
			filename: TARGET === 'build' ? '[name]-[hash].css' : '[name].css',
			chunkFilename: TARGET === 'build' ? '[id]-[hash].css' : '[id].css'
		}),
		new BundleTracker({
			path: target,
			filename: './webpack-stats.json'
		})
	]
};

if (TARGET === 'build') {
	module.exports = merge(common, {
		output: {
			filename: '[name]-[hash].js'
		},
		plugins: [
			new webpack.DefinePlugin({
				'process.env': { 'NODE_ENV': JSON.stringify('production') }
			})
		]
	});
}

if (TARGET === 'start') {
	module.exports = merge(common, {
		devtool: 'eval-source-map',
		devServer: {
			contentBase: target,
			progress: true,
		}
	});
}

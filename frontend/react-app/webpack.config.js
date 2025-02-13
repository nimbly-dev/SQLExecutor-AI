// webpack.config.js
const path = require('path');

module.exports = {
  // ...other config options...
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx', '.scss'],
    alias: {
      '@sqlexecutor-styles': path.resolve(__dirname, './src/styles'),
    },
  },
  module: {
    rules: [
      {
        test: /\.module\.scss$/,
        use: [
          'style-loader',
          {
            loader: 'css-loader',
            options: { modules: true },
          },
          'sass-loader',
        ],
      },
      // ...other rules...
    ],
  },
  // ...other config options...
};

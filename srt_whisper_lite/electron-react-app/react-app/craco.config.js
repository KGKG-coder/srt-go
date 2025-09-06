const path = require('path');

module.exports = {
  webpack: {
    configure: (webpackConfig, { env, paths }) => {
      if (env === 'production') {
        // 移除 source maps
        webpackConfig.devtool = false;
        
        // 優化分割
        webpackConfig.optimization = {
          ...webpackConfig.optimization,
          splitChunks: {
            chunks: 'all',
            cacheGroups: {
              vendor: {
                test: /[\\/]node_modules[\\/]/,
                name: 'vendors',
                chunks: 'all',
                maxSize: 244000, // 240KB
              },
            },
          },
        };

        // 排除不必要的模組
        webpackConfig.externals = {
          ...webpackConfig.externals,
          'react/jsx-dev-runtime': 'React.jsxDEV',
          'react/jsx-runtime': 'React.jsx',
        };
      }
      
      return webpackConfig;
    },
  },
};
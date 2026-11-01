// vue.config.js
module.exports = {
  devServer: {
    proxy: {
      '/pdf-proxy': {
        target: 'https://www.mozilla.org',
        changeOrigin: true,
        pathRewrite: {
          '^/pdf-proxy': ''
        }
      }
    }
  }
}
var isNode = require('is-node');
var nodeRequire = require;

module.exports = isNode ? nodeRequire('./lib/node') : require('./lib/browser');

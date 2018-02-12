var elasticsearch=require('elasticsearch');

var client = new elasticsearch.Client( {
  hosts: [
    process.env.ES_ENDPOINT
  ]
});

module.exports = client;

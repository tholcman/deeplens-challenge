var elasticsearch=require('elasticsearch');

var client = new elasticsearch.Client( {
  hosts: [
    'https://vpc-count-exercise-74dnkcubz7lddoh2uhkny362we.us-east-1.es.amazonaws.com/'
  ]
});

module.exports = client;



const endpoint = "http://34.230.47.42/"


var elasticsearch=require('elasticsearch');

var client = new elasticsearch.Client( {
  hosts: [
    endpoint
  ]
});

client.cluster.health({},function(err,resp,status) {  
    console.log("-- Client Health --",resp);
});

client.indices.create({  
    index: 'idx-exercises'
}, function(err,resp,status) {
    if(err) {
      console.log(err);
    }
    else {
      console.log("create",resp);
    }
});


var client = require('./conn.js');

exports.handler = function(event, context) {
    // var eventText = JSON.stringify(event, null, 2);
        
    // Log a message to the console, you can view this text in the Monitoring tab in the Lambda console or in the CloudWatch Logs console
    // console.log("Received event:", eventText);
    /*
    {
        "type": "exercise",
        "payload": {
            "id": "",// uuid
            "camera": "deeplens_c87d5d0b-c7b1-4d20-af10-8b1b1e035f59",
            "time": "1518365499.94",
            "exercise": "barbell_up"
        }
    }
    */
    if (event.type != "exercise") {
        // for now we don't want to log system messages
        return
    }
    
    client.index({  
        index: 'idx-exercise',
        id: event.payload.id,
        type: event.type,
        body: event.payload
    }, function(err,resp,status) {
          console.log(resp);
    });
    
}

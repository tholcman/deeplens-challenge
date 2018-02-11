## get-json

Cross-platform library for getting JSON documents. Wraps [request](http://npmjs.org/request) on Node, fallsback to [JSONP](http://github.com/webmodules/jsonp) on browsers.

```bash
$ npm install get-json
```

## Usage

```js
var getJSON = require('get-json')

getJSON('http://api.listenparadise.org', function(error, response){

    error
    // undefined

    response.result
    // ["Beth Orton &mdash; Stolen Car",
    // "Jack White &mdash; Temporary Ground",
    // "I Am Kloot &mdash; Loch",
    // "Portishead &mdash; Glory Box"]

    response.ok
    // => true

})
```

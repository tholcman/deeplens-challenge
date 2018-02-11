# Exercise counter with Deeplens

Original idea was to have camera which will count exercises on machines for bench press, lat pulldown, chest press etc. in gym. And mobile/web app which will show personal statistics. During development I got stuck many times on training, deployments, model conversions etc. I am not python developer and I didn't have any knowledge about machine learning. At the end I was able to create just simple model which can recognize barbell and from its moves it tries to count exercises. Logs about exercises are sent via IoT to Lambda which saves them to Elasticsearch. Unfortunetely I was not able to create any frontend. Exercises logs might be seen just in Kibana. If you ask I can add your IP address to firewall and send you Kibana endpoint to see results.

## Requiremnts


## Project structure

```
./
├── count-exercise # lambda to be deployed to Deeplens
├── pass-to-es # lambda to pass data from IoT topic to Elasticsearch, probably should be renamed and used for ES-mobile interface
├── terraform # terraform for other resources
└── training # notes on training and converting model
```
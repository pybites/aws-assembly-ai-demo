# AWS + Assembly AI demo

Demo to create an S3 bucket with trigger to invoke a lambda function to transcribe an audio file using Assembly AI.

For `requests` I used a layer from [here](https://github.com/keithrozario/Klayers).

In the config/ directory there are config settings for 1. the bucket to make files public (needed for Assembly AI, tried signed urls, but that did not work), and 2. for the lambda function to post the srt file back to the bucket.

TODO: be able to test a lambda function locally, e.g. using `sam local invoke MyLambdaFunction --event test/event.json --region us-east-2` (this did not work well yet with the defined layer in template.yaml)

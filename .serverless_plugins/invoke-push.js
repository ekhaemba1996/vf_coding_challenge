'use strict';
const aws = require('aws-sdk');

// Get the lambda client from the sdk
const getLambdaClient = serverless => {
  aws.config.update({
    region: serverless.service.provider.region
  });
  return new aws.Lambda();
}

const invokeLambda = (serverless, options) => new Promise((resolve, reject)=>{
  serverless.cli.log('Beginning invoke lambda function');
  const functionName = serverless.service.functions.pushToDynamo.name;
  const lambdaClient = getLambdaClient(serverless);
  const params = {
    FunctionName: functionName,
    Payload: "{}"
  };

  lambdaClient.invoke(params, function(err,data){
    if(err){
      serverless.cli.log(`Function ${functionName} failed on invocation`);
      return reject(err);
    }
    serverless.cli.log(`Function ${functionName} invoked successfully`);
    return resolve();
  });
});

class InvokePlugin {
  constructor(serverless, options) {
    this.serverless = serverless;
    this.options = options;
    this.hooks = {
      'after:deploy:deploy': invokeLambda.bind(null, serverless, options)
    };
  }
}

module.exports = InvokePlugin;

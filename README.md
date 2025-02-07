# Voice Foundry Coding Challenge
### Description
This is the repository for the Voice Foundry Coding Challenge. I created this deployment to serve as a pokemon detail api service. 

### Problem Statement

For those who are unfamiliar with [pokemon](https://en.wikipedia.org/wiki/Pok%C3%A9mon_(video_game_series)) it is a Japanese Role-playing video game series centered on the collection and training of a team of Pocket Monsters (pokemon). Each pokemon you collect has a set of physical attributes and types that make it more effective or less effective when fighting other pokemon. 

In each game the player is tasked with developing their team of pokemon for the purpose of beating a series of rival trainers, story related villains and gym leaders. Maintaining a balanced team of pokemon that are each specialized in defeating a specific type of enemy is generally the best strategy to use when playing the game. In-fact the biggest advantage you as a player has when determining the effectiveness of your pokemon vs. another is your type effectiveness against enemy types. 

This type chart explains explicitly what pokemon types are effective against other pokemon types. 

![Pokemon type chart](https://img.rankedboost.com/wp-content/uploads/2016/11/sun-and-moon-type-chart-2.jpg)

When I started playing the series back in the early 2000's there were only 3 generations of pokemon totalling about 350 pokemon. For any kid that wanted to be effective at the game it was nearly a requirement to memorize not only this type chart but also the types of every pokemon you encountered on sight. Now there are about 8 generations of pokemon totalling nearly 900. Albeit not every game included all the pokemon that existed in previous games and coincidentally the developers themselves said they're no longer prioritizing supporting [older generation pokemon](https://www.businessinsider.com/pokemon-sword-shield-nintendo-switch-2019-6). I wanted to make this api as a response to the struggles of younger me and his dedication to becoming the very best pokemon master.

Examples of the I would have were:
* I am about to fight a gym that specializes in Fighting what are some Flying type pokemon I can get to help me?
* My team could sure use a Fire pokemon to balance it out, what can I choose?
* Where can I get Poison pokemon?

The dataset I used in this deployment was extracted from kaggle [https://www.kaggle.com/abcsds/pokemon](https://www.kaggle.com/abcsds/pokemon)
### Deployment instructions
Utilizing the serverless framework and npm you should be able to deploy the stack by first running `npm install` and subsequently running `serverless deploy` in the shell of your choosing. 

One potential caveat is you may need to install the serverless version 2.4.0 via `npm install serverless@2.4.0 -g`

### Key functionality
Upon executing a `serverless deploy` the s3 sync plugin should execute and sync the pokemon dataset to an s3 bucket using the `serverless-s3-sync` plugin. After which the custom plugin will invoke the data ingest lambda to parse the s3 file and push to a dynamo db table.

Two endpoints were developed for this deployment.
1. /get_pokemon_by_type/{type}
    * Given a type this endpoint will return a set of pokemon that correspond to that type. Optionally you can also provide two query parameters.
        * min_sum (Integer) - Corresponds to the minimum total stats the resultant pokemon have.
            * I.E. - Beldum will be excluded on the following URI `/get_pokemon_by_type/Steel?min_sum=400` and included on this one `/get_pokemon_by_type/Steel`
        * secondary (Constant value 'true') - If set to true the pokemon returned will have the secondary type of the type passed instead of the primary.
            * I.E. - Lucario will be included when a GET request is made on the following URI `/get_pokemon_by_type/Steel?secondary=true`

### Lessons learned
I took a lot of takeaways from Alex DeBrie's talk on [structuring Dynamo tables](https://www.youtube.com/watch?v=DIQVJqiSUkE&feature=youtu.be&t=831). Initially during my development of this table I had begun normalizing the DDB records as I would if structuring a relational Database. I did this especially for the use case of finding what secondary or primary types correspond to which pokemon. However, after I had watched this talk I began to see how potentially problematic that was going to become. His point about knowing up-front what questions you need to answer is extremely important as that will drive the design of the object entity records in the database. 

If I wanted to expand on this in the future to include information regarding pokemon moves in each generation I would need to judiciously structure my keys to allow for such a relationship that can easily be queried on. I find the single table design to be fascinating and a really interesting challenge. I also really appreciated the plugin when I was designing the schema for the table as it helped me easily take down and stand up the table and automatically ingest the data on every serverless deploy.

### Potential Actions and Enhancements
The amount of pokemon that exist today are not a lot (not even 1000 distinct records), however these pokemon have a lot of interesting attributes and data relationships that gamers would want to be easily searchable. For instance the most popular pokemon Pikachu was created in the first generation but it can appear in subsequent generations. Another Entity Object I would want to track is the location of where players can find each of these pokemon depending on the game that they are playing. 

That on its own has the potential for blowing up the record count ten-fold. Given that information I would want to enhance my current data ingestion lambda to be decoupled to involve an intermediary ingestion SQS queue. A set of S3 files can be parsed, batched and have its records pushed to an sqs queue after which the records in the queue will be processed in batches into dynamo db. Along with a better data ingestion flow a schema redesign would undoubtedly need to happen to account for this one to many relationship between pokemon and their location per generation. especially if this is pertinent information I want to query on.

A nice style feature I would love to have is to host this service under a specific domain and I know that is [possible](https://www.serverless.com/blog/serverless-api-gateway-domain) with some serverless plugins. Something cute along the lines of `pokeserv.io`
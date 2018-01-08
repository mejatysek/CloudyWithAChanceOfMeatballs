# Cloudy with a chance of meatballs
Mashup app providing weather forecast displayed on map only for cities specified by user.

Semestral project for A4M33VIA class at CTU

## App description
It's simple app displaying one day weather forecast for user's selected cities over google map.

## Apis
### Used
 * [AccuWauther](https://developer.accuweather.com/accuweather-locations-api/apis)
 * [Google maps](https://developers.google.com/maps/)

### Provided
Api provide weather icon's with embeded temperature and forecast's for user's cities extended with geolocation and link to icon endpoint.
#### Documentation:
  * [swagger](https://app.swaggerhub.com/apis/CTU17/cloudy_with_a_chance_of_meatballs/1.0.0)

## Technologies
### App
![AppTech](https://github.com/mejatysek/CloudyWithAChanceOfMeatballs/blob/master/doc/tech_app.png)
### Deployment
![DeploymentTech](https://github.com/mejatysek/CloudyWithAChanceOfMeatballs/blob/master/doc/tech_deploy.png)

## Challenges
 * AcuWeather api rate limit
 * Google Maps markers can't be complex objects

## Deployment
App deloyed at [via.mejty.cz](https://via.mejty.cz/).

For deploy own copy use any of [Flask deploy options](http://flask.pocoo.org/docs/0.12/deploying/).
Before run app is necesary add credential file to `webapp/credentials.json` with your acuWeather and Google maps API keys.

### Credentials file
```json
{
  "maps": "$YourAcuWeatherApiKey",
  "acuweather": "$YourGoogleMapsApiKey"
}
```

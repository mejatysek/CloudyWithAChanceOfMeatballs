from pathlib import Path
from string import Template
from decimal import Decimal

from flask import Flask, render_template, redirect, request, jsonify, Response, url_for

from creds import Credentials
from store import Store
from weatherApi import WeatherApi

app = Flask(__name__)

store = Store()
credentials = Credentials()
weatherApi = WeatherApi(store)


@app.route('/')
def index():
    user_id = request.args.get('userid', '', type=str)
    if store.id_exists(user_id):
        return redirect(url_for('main', user_id=user_id), code=302)
    else:
        return render_template('index.html', user_id=user_id)


@app.route('/id/')
def gen_id():
    new_id = store.get_new_id()
    return redirect(url_for('main', user_id=new_id), code=302)


@app.route('/<user_id>/')
def main(user_id):
    if store.id_exists(user_id):
        cities = store.get_user_cities(user_id)
        forecasts = []
        for k, v in cities.items():
            forecasts.append({"id": k, "lat": v['latitude'], "long": v['longitude'], "name": v['name'], "icon": "/icon/{k}/".format(k=k)})
        return render_template(
            "forecast.html",
            map_key=credentials.maps_key,
            user_id=user_id, cities=cities,
            forecasts=forecasts,
            show_id=store.show_user_message(user_id))
    else:
        return redirect("/", code=302)


@app.route('/city/search/')
def search_city():
    query = request.args.get('q', '', type=str)
    if len(query) > 3:
        result = weatherApi.search_city(query).get("results", [])
        data = {"results": [{"id": v["id"], "text": "{city}({country})".format(city=v['name'], country=v['country_code'])} for v in result]}
        return jsonify(data)


@app.route('/<user_id>/city/<location_key>/add/')
def add_city(user_id, location_key):
    if store.id_exists(user_id):
        city = weatherApi.get_city_by_id(location_key)
        store.add_user_city(user_id, city)
        return redirect(url_for('main', user_id=user_id))
    else:
        redirect("/", code=302)


@app.route('/<user_id>/city/<location_key>/del/')
def del_city(user_id, location_key):
    if store.id_exists(user_id):
        store.del_user_city(user_id, location_key)
        return redirect(url_for('main', user_id=user_id))
    else:
        redirect("/", code=302)


@app.route('/icon/<location_key>/')
def forecast_icon(location_key):
    city = weatherApi.get_city_by_id(location_key)

    forecast = weatherApi.get_day_forecast(city["latitude"], city["longitude"])
    icon_num =  forecast['daily']['weathercode'][0]
    with open("static/icons/{num}.svg".format(num=icon_num)) as icon:
        icon_data = Template(icon.read())
        result = icon_data.substitute(min='{0: >2}'.format(str(round(Decimal(forecast['daily']['temperature_2m_min'][0])))),
                                      max=str(round(Decimal(forecast['daily']['temperature_2m_max'][0]))))
        return Response(response=result, status=200, mimetype="image/svg+xml")


@app.route('/<user_id>/forecast/')
def api_forecast(user_id):
    if store.id_exists(user_id):
        cities = store.get_user_cities(user_id)
        result = []
        for k, v in cities.items():
            forecast = weatherApi.get_day_forecast(v["latitude"], v["longitude"])
            forecast_icon_url = "/icon/{k}/".format(k=k)
            daily_forecast = {
                "Date": forecast["daily"]["time"][0],
                "Temperature": {
                    "Minimum": {"Value": forecast["daily"]["temperature_2m_min"][0]},
                    "Maximum": {"Value": forecast["daily"]["temperature_2m_max"][0]},
                },
                "Day": {"Icon": forecast["daily"]["weathercode"][0]}
            }
            cloudy_data = {'Name': v['name'], 'GeoPosition': {'Latitude': v['latitude'], 'Longitude': v['longitude']}, 'ForecastIconUrl': forecast_icon_url}
            result.append({"DailyForecasts": [daily_forecast], "Cloudy": cloudy_data})
        return jsonify(result)
    else:
        return Response("Bad id", status=404)


if __name__ == '__main__':
    app.run()

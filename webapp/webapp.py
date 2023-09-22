from pathlib import Path
from string import Template
from decimal import Decimal

from flask import Flask, render_template, redirect, request, jsonify, Response

from creds import Credentials
from store import Store
from weatherApi import WeatherApi

app = Flask(__name__)

store = Store()
credentials = Credentials()
acuAPI = WeatherApi(store, credentials)


@app.route('/')
def index():
    user_id = request.args.get('userid', '', type=str)
    if store.id_exists(user_id):
        return redirect("/{user_id}/".format(user_id=user_id), code=302)
    else:
        return render_template('index.html', user_id=user_id)


@app.route('/id/')
def gen_id():
    new_id = store.get_new_id()
    return redirect("/{user_id}/".format(user_id=new_id), code=302)


@app.route('/<user_id>/')
def main(user_id):
    if store.id_exists(user_id):
        cities = store.get_user_cities(user_id)
        forecasts = []
        for k, v in cities.items():
            forecasts.append({"id": k, "lat": v['GeoPosition']['Latitude'], "long": v['GeoPosition']['Longitude'], 'icon': "/icon/{k}/".format(k=k)})
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
        result = acuAPI.search_city(query)
        data = {"results": [{"id": v["Key"], "text": "{city}({country})".format(city=v['LocalizedName'], country=v['Country']['ID'])} for v in result]}
        return jsonify(data)


@app.route('/<user_id>/city/<location_key>/add/')
def add_city(user_id, location_key):
    if store.id_exists(user_id):
        city = acuAPI.get_city(location_key)
        store.add_user_city(user_id, city)
        return redirect("/{user_id}/".format(user_id=user_id))
    else:
        redirect("/", code=302)


@app.route('/<user_id>/city/<location_key>/del/')
def del_city(user_id, location_key):
    if store.id_exists(user_id):
        store.del_user_city(user_id, location_key)
        return redirect("/{user_id}/".format(user_id=user_id))
    else:
        redirect("/", code=302)


@app.route('/icon/<location_key>/')
def forecast_icon(location_key):
    forecast = acuAPI.get_5_day_forecast(location_key)['DailyForecasts'][0]
    icon_num = forecast['Day']['Icon']
    with open("static/icons/{num}.svg".format(num=icon_num)) as icon:
        icon_data = Template(icon.read())
        result = icon_data.substitute(min='{0: >2}'.format(str(round(Decimal(forecast['Temperature']['Minimum']['Value'])))),
                                      max=str(round(Decimal(forecast['Temperature']['Maximum']['Value']))))
        return Response(response=result, status=200, mimetype="image/svg+xml")


@app.route('/<user_id>/forecast/')
def api_forecast(user_id):
    if store.id_exists(user_id):
        cities = store.get_user_cities(user_id)
        result = []
        for k, v in cities.items():
            forecast = acuAPI.get_5_day_forecast(k)
            forecast_icon_url = "/icon/{k}/".format(k=k)
            forecast['DailyForecasts'] = forecast['DailyForecasts'][0]
            forecast['Cloudy'] = {'Name': v['LocalizedName'], 'GeoPosition': v['GeoPosition'], 'ForecastIconUrl': forecast_icon_url}
            result.append(forecast)
        return jsonify(result)
    else:
        return Response("Bad id", status=404)


if __name__ == '__main__':
    app.run()

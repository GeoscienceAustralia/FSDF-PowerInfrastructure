from flask import Blueprint, request, Response, render_template
from model.power_line import Power_line
from model.power_station import Power_station
from model.power_substation import Power_substation
from pyldapi import ContainerRenderer
import conf
import ast
import folium
import os, yaml
import webbrowser
import requests

print(__name__)
routes = Blueprint('controller', __name__)

DEFAULT_ITEMS_PER_PAGE=50

@routes.route('/fsdf_home', strict_slashes=True)
def fsdf_home():
    # webbrowser.open('https://geoscienceaustralia.github.io/FSDF/')
    # requests.get('https://geoscienceaustralia.github.io/FSDF/')
    # return render_template('home.html', home_page_settings=conf.home_page_boxes_dict)
    return render_template('fsdf_home.html')


@routes.route('/', strict_slashes=True)
def home():
    return render_template('home.html', home_page_settings=conf.home_page_boxes_dict)


@routes.route('/power_lines/')
def power_lines():
    # Search specific items using keywords
    search_string = request.values.get('search')

    try:

        # get the register length from the online DB
        sql = 'SELECT COUNT(*) FROM "Transmission_linesV3source84"'
        if search_string:
            sql += '''WHERE UPPER(cast("id" as text)) LIKE '%{search_string}%' OR UPPER("NAME") LIKE '%{search_string}%';
                   '''.format(search_string=search_string.strip().upper())

        no_of_items = conf.db_select(sql)[0][0]

        page = int(request.values.get('page')) if request.values.get('page') is not None else 1
        per_page = int(request.values.get('per_page')) \
                   if request.values.get('per_page') is not None else DEFAULT_ITEMS_PER_PAGE
        offset = (page - 1) * per_page

        # get the id and name for each record in the database
        sql = '''SELECT "id", "NAME" FROM "Transmission_linesV3source84"'''
        if search_string:
            sql += '''WHERE UPPER(cast("id" as text)) LIKE '%{search_string}%' OR UPPER("NAME") LIKE '%{search_string}%'
                   '''.format(search_string=search_string.strip().upper())
        sql += '''ORDER BY "NAME"
                OFFSET {} LIMIT {}'''.format(offset, per_page)

        items = []
        for item in conf.db_select(sql):
            items.append(
                (item[0], item[1])
            )
    except Exception as e:
        print(e)
        return Response('The power database is offline', mimetype='text/plain', status=500)

    return ContainerRenderer(request=request,
                            instance_uri=request.url,
                            label='Power Line Register',
                            comment='A register of Power Lines',
                            parent_container_uri='http://linked.data.gov.au/def/placenames/PlaceName',
                            parent_container_label='Power Line',
                            members=items,
                            members_total_count=no_of_items,
                            profiles=None,
                            default_profile_token=None,
                            super_register=None,
                            page_size_max=1000,
                            register_template=None,
                            per_page=per_page,
                            search_query=search_string,
                            search_enabled=True
                            ).render()


@routes.route('/power_lines/<string:power_line_id>')
def power_line(power_line_id):
    power_line = Power_line(request, request.base_url)
    return power_line.render()


@routes.route('/power_stations/')
def power_stations():
    # Search specific items using keywords
    search_string = request.values.get('search')

    try:

        # get the register length from the online DB
        sql = 'SELECT COUNT(*) FROM "powerStationPointsSource84"'
        if search_string:
            sql += '''WHERE UPPER(cast("id" as text)) LIKE '%{search_string}%' OR UPPER("name") LIKE '%{search_string}%';
                   '''.format(search_string=search_string.strip().upper())

        no_of_items = conf.db_select(sql)[0][0]

        page = int(request.values.get('page')) if request.values.get('page') is not None else 1
        per_page = int(request.values.get('per_page')) \
                   if request.values.get('per_page') is not None else DEFAULT_ITEMS_PER_PAGE
        offset = (page - 1) * per_page

        # get the id and name for each record in the database
        sql = '''SELECT "id", "name" FROM "powerStationPointsSource84"'''
        if search_string:
            sql += '''WHERE UPPER(cast("id" as text)) LIKE '%{search_string}%' OR UPPER("name") LIKE '%{search_string}%'
                   '''.format(search_string=search_string.strip().upper())
        sql += '''ORDER BY "name"
                OFFSET {} LIMIT {}'''.format(offset, per_page)

        items = []
        for item in conf.db_select(sql):
            items.append(
                (item[0], item[1])
            )
    except Exception as e:
        print(e)
        return Response('The power database is offline', mimetype='text/plain', status=500)

    return ContainerRenderer(request=request,
                            instance_uri=request.url,
                            label='Power Station Register',
                            comment='A register of Power Stations',
                            parent_container_uri='http://linked.data.gov.au/def/placenames/PlaceName',
                            parent_container_label='Power Station',
                            members=items,
                            members_total_count=no_of_items,
                            profiles=None,
                            default_profile_token=None,
                            super_register=None,
                            page_size_max=1000,
                            register_template=None,
                            per_page=per_page,
                            search_query=search_string,
                            search_enabled=True
                            ).render()


@routes.route('/power_stations/<string:power_station_id>')
def power_station(power_station_id):
    power_station = Power_station(request, request.base_url)
    return power_station.render()


@routes.route('/power_substations/')
def power_substations():
    # Search specific items using keywords
    search_string = request.values.get('search')

    try:

        # get the register length from the online DB
        sql = 'SELECT COUNT(*) FROM "power_substation_points84"'
        if search_string:
            sql += '''WHERE UPPER(cast("id" as text)) LIKE '%{search_string}%' OR UPPER("name") LIKE '%{search_string}%';
                   '''.format(search_string=search_string.strip().upper())

        no_of_items = conf.db_select(sql)[0][0]

        page = int(request.values.get('page')) if request.values.get('page') is not None else 1
        per_page = int(request.values.get('per_page')) \
                   if request.values.get('per_page') is not None else DEFAULT_ITEMS_PER_PAGE
        offset = (page - 1) * per_page

        # get the id and name for each record in the database
        sql = '''SELECT "id", "name" FROM "power_substation_points84"'''
        if search_string:
            sql += '''WHERE UPPER(cast("id" as text)) LIKE '%{search_string}%' OR UPPER("name") LIKE '%{search_string}%'
                   '''.format(search_string=search_string.strip().upper())
        sql += '''ORDER BY "name"
                OFFSET {} LIMIT {}'''.format(offset, per_page)

        items = []
        for item in conf.db_select(sql):
            items.append(
                (item[0], item[1])
            )
    except Exception as e:
        print(e)
        return Response('The power database is offline', mimetype='text/plain', status=500)

    return ContainerRenderer(request=request,
                            instance_uri=request.url,
                            label='Power Station Register',
                            comment='A register of Power Stations',
                            parent_container_uri='http://linked.data.gov.au/def/placenames/PlaceName',
                            parent_container_label='Power Substation',
                            members=items,
                            members_total_count=no_of_items,
                            profiles=None,
                            default_profile_token=None,
                            super_register=None,
                            page_size_max=1000,
                            register_template=None,
                            per_page=per_page,
                            search_query=search_string,
                            search_enabled=True
                            ).render()


@routes.route('/power_substations/<string:power_substation_id>')
def power_substation(power_substation_id):
    power_substation = Power_substation(request, request.base_url)
    return power_substation.render()


@routes.route('/map')
def show_map():
    '''
    Function to render a map around the specified line
    '''

    name = request.values.get('name')
    coords_list = ast.literal_eval(request.values.get('coords'))

    if len(coords_list) == 1:  #polyline
        # swap x & y for mapping
        points = []
        for coords in coords_list[0]:
            points.append(tuple([coords[1], coords[0]]))

        ave_lat = sum(p[0] for p in points) / len(points)
        ave_lon = sum(p[1] for p in points) / len(points)

        # create a new map object
        folium_map = folium.Map(location=[ave_lat, ave_lon], zoom_start=15)
        tooltip = 'Click for more information'

        folium.PolyLine(points, color="red", weight=2.5, opacity=1, popup = name, tooltip=tooltip).add_to(folium_map)
    else: #point
        # create a new map object
        lat = coords_list[1]
        lon = coords_list[0]
        folium_map = folium.Map(location=[lat, lon], zoom_start=15)
        tooltip = 'Click for more information'
        folium.Marker([lat, lon], popup=name, tooltip=tooltip).add_to(folium_map)

    return folium_map.get_root().render()





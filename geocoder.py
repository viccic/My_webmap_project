import folium
import folium.plugins
import requests
import streamlit as st
from streamlit_folium import folium_static
import time
import networkx as nx
import osmnx as ox


st.title("Victoria's Geocoder")
st.markdown('This app uses the [OpenRouteService](https://openrouteservice.org) API to geocode a location and display the OpenStreetMap streets of this location on a map.')
address = st.text_input("Search...")

ORS_API_KEY = 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImJkYWNjYTRiMTM4NTQ1YzZiNTFkYzgwYTdlMTE4YzhlIiwiaCI6Im11cm11cjY0In0='

@st.cache_data
def geocode(query):
    parameters = {
        'api_key': ORS_API_KEY,
        'text': query
    }
    response = requests.get(
        'https://api.openrouteservice.org/geocode/search',
        params=parameters
    )
    if response.status_code == 200:
        data = response.json()
        if data['features']:
            x, y = data['features'][0]['geometry']['coordinates']
            return (y, x)
if address:
    results = geocode(address)

    if results:
        # Calculate the start time
        start = time.time()
        st.write(
            "Geocoded Coordinates: {}, {}".format(results[0], results[1]))
        m = folium.Map(location=results, zoom_start=13, control_scale=True, zoom_control=False)

        # folium.Marker(
        #     results,
        #     popup=address,
        #     icon=folium.Icon(color="green", icon="crosshairs", prefix="fa")
        # ).add_to(m)


        # download/model a street network for some city then visualize it
        G = ox.graph_from_place(address, network_type='drive')
        # fig, ax = ox.plot.plot_graph(G)

        # # you can convert your graph to node and edge GeoPandas GeoDataFrames
        gdf_nodes, gdf_edges = ox.convert.graph_to_gdfs(G)
        # gdf_edges.head()

        # extract OSM polygon
        gdf_polygon = ox.geocoder.geocode_to_gdf(address)

        folium.GeoJson(
            gdf_edges,
            name="OSM streets",
            popup=folium.GeoJsonPopup(fields=["name","maxspeed"]),
            style_function=lambda feature: {
                "color": "#3388ff",
                "weight": 2,
            },
            highlight_function=lambda feature: {
                "color": "#ffff00",
                "weight": 4,
            },
        ).add_to(m)

        folium.GeoJson(
            gdf_polygon,
            name="Boundary",
            style_function=lambda feature: {
                "color": "#ff0000",
                "weight": 2,
                "fill": False,
            }
        ).add_to(m)

        folium.LayerControl(collapsed=False).add_to(m)
        folium_static(m, width=800)

        m.save("StreetsIn" + address + ".html")
        # Calculate the end time and time taken
        end = time.time()
        length = end - start

        # Show the results : this can be altered however you like
        print("It took", length, "seconds!")

    else:
        st.error("Request failed. No results.")



# # gdf_edges["maxspeed"].apply(type).value_counts()
#

#
# folium.plugins.Geocoder().add_to(m)
#



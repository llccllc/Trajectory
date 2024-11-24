from geopy.distance import distance
import math

min_lat, max_lat = 39.4, 41.6
min_lon, max_lon = 115.7, 117.4

n = 20


def calculate_grid_sizes():
    lat_distance_km = distance((min_lat, min_lon), (max_lat, min_lon)).km
    lat_grid_size_km = lat_distance_km / n

    lon_distance_km = distance((min_lat, min_lon), (min_lat, max_lon)).km
    m = int(lon_distance_km / lat_grid_size_km)

    return lat_grid_size_km, m


def lat_lon_to_grid(lat, lon, lat_grid_size_km, m):
    lat_distance = distance((min_lat, min_lon), (lat, min_lon)).km
    grid_i = math.floor(lat_distance / lat_grid_size_km)

    lon_distance = distance((min_lat, min_lon), (min_lat, lon)).km
    grid_j = math.floor(lon_distance / lat_grid_size_km)

    grid_j = min(grid_j, m - 1)

    return grid_i, grid_j


def process_trajectory(input_file, output_file):
    lat_grid_size_km, m = calculate_grid_sizes()

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            trajectory_id, points = line.split(':')
            points = points.strip().split(')(')
            points[0] = points[0].replace('(', '')
            points[-1] = points[-1].replace(')', '')

            grid_points = []
            for point in points:
                lat, lon = map(float, point.split(','))
                grid_i, grid_j = lat_lon_to_grid(lat, lon, lat_grid_size_km, m)
                grid_points.append(f"({grid_i},{grid_j})")

            outfile.write(f"{trajectory_id}:{''.join(grid_points)}\n")

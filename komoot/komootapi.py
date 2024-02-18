import requests
from komoot.gpxcompiler import GpxCompiler


class KomootApi:
	def __init__(self):
		pass

	@staticmethod
	def __send_request(url):
		r = requests.get(url)
		return r

	@staticmethod
	def sanitize_filename(value):
		for c in '\\/:*?"<>|':
			value = value.replace(c, '')
		return value

	def fetch_tour(self, tour_id, share_token):
		print("Fetching tour '" + tour_id + "'...")
		r = self.__send_request("https://api.komoot.de/v007/tours/" + tour_id + "?_embedded=coordinates,way_types,"
																				"surfaces,directions,participants,"
																				"timeline&directions=v2&fields"
																				"=timeline&format=coordinate_array"
																				"&timeline_highlights_fields=tips,"
																				"recommenders&share_token=" + share_token)
		return r.status_code, r.json()

	def make_gpx(self, tour, add_date=False):
		gpx = GpxCompiler(tour)

		# Example date: 2022-01-02T12:26:41.795+01:00
		# :10 extracts "2022-01-02" from this.
		date_str = tour['date'][:10]+'_' if add_date else ''

		return gpx.generate(), f"{date_str}{self.sanitize_filename(tour['name'])}-{tour['id']}.gpx"

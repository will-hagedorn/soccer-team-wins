import matchdb_pb2, matchdb_pb2_grpc, grpc
from concurrent import futures
import pandas as pd
import sys
import socket

class MyMatchCount(matchdb_pb2_grpc.MatchCountServicer):
	def __init__(self, data):
		self.data = data

	def GetMatchCount(self, request, context):
		team_filter = request.winning_team
		country_filter = request.country

		filtered_df = self.data.copy()

		if (country_filter and country_filter != "nan"):
			filtered_df = filtered_df[filtered_df['country'] == country_filter]

		if (team_filter and team_filter != "nan"):
			filtered_df = filtered_df[filtered_df['winning_team'] == team_filter]

		return matchdb_pb2.GetMatchCountResp(num_matches = len(filtered_df))

def getServer():
	ip = socket.gethostbyname(socket.gethostname())
	ipServer1 = socket.gethostbyname("wins-server-1")
	ipServer2 = socket.gethostbyname("wins-server-2")

	if (ip == ipServer1):
		return 'partitions/part_0.csv', 'wins-server-1'
	elif (ip == ipServer2):
		return 'partitions/part_1.csv', 'wins-server-2'

def loadCLA():

	if (len(sys.argv) == 3):
		csvPath = sys.argv[1]
		port = sys.argv[2]
	else:
		csvPath, serverNum = getServer()
		port = '5440'

	csvData = pd.read_csv(csvPath)

	return csvData, port

def server():
	#Reads data and gets port
	data, port = loadCLA()

	print("start server")
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=1), options=[("grpc.so_reuseport", 0)])

	matchdb_pb2_grpc.add_MatchCountServicer_to_server(MyMatchCount(data), server)

	server.add_insecure_port("[::]:" + str(port))
	server.start()
	print(f'Server started on port {port} using {data}')
	server.wait_for_termination()

if __name__ == "__main__":
    server()

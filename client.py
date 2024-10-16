import grpc, matchdb_pb2_grpc, matchdb_pb2
import sys
import pandas as pd
from collections import OrderedDict


def simple_hash(country):
	out = 0
	for c in country:
        	out += (out << 2) - out + ord(c)

	return out

def requester(stub, country, winning_team):
	resp = stub.GetMatchCount(matchdb_pb2.GetMatchCountReq(country = country, winning_team = winning_team))

	return resp.num_matches

def process_input(stub0, stub1, input_file, cache):
	data = pd.read_csv(input_file)
	data = data.reset_index()

	for i in data.index:
		country = str(data['country'][i])
		winning_team = str(data['winning_team'][i])

		# Concatenate team and country hash for caching
		team_cache = (winning_team, country)

		# Check if already in cache
		if (team_cache in cache):
			temp = cache[team_cache]

			print(str(temp) + "*")

			# Move team to front of cache
			cache.move_to_end(team_cache)
			cache[team_cache] = temp

			continue

		# Makes requests based on country hash
		total = 0
		if (country != "" and country != "nan"):
			server_num = simple_hash(country) % 2
			if (server_num == 0):
				total = requester(stub0, country, winning_team)
			else:
				total = requester(stub1, country, winning_team)
		else:
			count1 = requester(stub0, country, winning_team)
			count2 = requester(stub1, country, winning_team)

			total = count1 + count2

		# Place team in cache
		if (len(cache) < 10):
			cache[team_cache] = total
		else:
			cache.popitem(last=False)
			cache[team_cache] = total
		print(total)

def client():
	serve0 = sys.argv[1]
	serve1 = sys.argv[2]
	input_file = sys.argv[3]

	channel0 = grpc.insecure_channel(serve0)
	channel1 = grpc.insecure_channel(serve1)

	stub0 = matchdb_pb2_grpc.MatchCountStub(channel0)
	stub1 = matchdb_pb2_grpc.MatchCountStub(channel1)

	# For cache
	cache = OrderedDict()

	process_input(stub0, stub1, input_file, cache)

if __name__ == "__main__":
	client()

class rou :
	def Dijkstra(self,startNode, endNode, graphdict=None):
		book = set()
		minv = endNode
# 源頂點到其餘各頂點的初始路程
		dis = dict((k,INF) for k in G.keys())
		dis[v0] = 0
		while len(book)<len(G):
			book.add(minv)         # 確定當期頂點的距離
		for w in G[minv]:        # 以當前點的中心向外擴散
			if dis[minv] < dis[w]:   # 如果從當前點擴充套件到某一點的距離小與已知最短距離
				dis[w] = dis[minv]   # 對已知距離進行更新
				new = INF          # 從剩下的未確定點中選擇最小距離點作為新的擴散點
		for v in dis.keys():
			if v in book: 
				continue
			if dis[v] < new:
				new = dis[v]
				minv = v
		return dis

G={"ANNUMINAS":[("FORNOST",12)],
"FORNOST":[("BREE",11),("ANNUMINAS",12),("HOBBITON",17),("GREYHAVENS",39)],
"HOBBITON":[("FORNOST",17),("BREE",12),("ICHELDELVING",2)],
"GREYHAVENS":[("MICHELDELVING",14),("FORNOST",39)],
"BREE":[("FORNOST",11),("HOBBITON",13),("TARBAD",21)],
"MICHELDELVING":[("HOBBITON",2),("TARBAD",31)],
"TARBAD":[("MICHELDELVING",31),("BREE",21)]}


shortestRoad = rou.Dijkstra ("ANNUMINAS","BREE",G)


print(shortestRoad.values()) 





networkx-pandas (mushed together, experimental)
---------------

The auction holds all the live data, buyers and sellers
and passes a dataframe up to the auctioneer every time a 
players price changes. The memory in the auction is flash, 
and is updated the next time a player challenges the price.

The auctioneer tells the auction where it is in time w.r.t to 
the round it is playing, and stores history of how player's 
connectivity influences the price over time. The auctioneer 
also controls the clock, which determines where in time the price
was influenced by previous rounds.

Run the test.py script for an interactive shell with some nodes, an auction, and an auctioneer.
The parameters are stored in csv, edit them like:

```
	values = pd.read_csv('./params/params.dat')
	values.loc[0,'nbuyers']=25
	values.loc[0,'sellers']=17
	f = open('./params/params.dat','w')
	f.write(values.to_csv(index=False).strip())
	f.close()
	params=make_params()

```
The variables in the shell are:
**Nested Nodes**
```
	nd, nds = test_node(params)
```
**Auction Objects**
```
	g = test_auction()
	n=g._node
	e=g._adj
```
**Auctioneer Objects**
```
print("Passed auction test...")
	G = test_auctioneer()
	N=G._node
	E=G._adj
	G.run_auctions(0)

```
**Market Object**
This should keep running until you stop it.
```
	sim = MarketSim(make_params)
	rnum=0
	while True:
		sim.do_round(rnum)
		rnum+=1
```

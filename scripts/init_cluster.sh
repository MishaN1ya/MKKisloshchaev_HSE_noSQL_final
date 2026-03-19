#!/bin/bash
set -e

sleep 10

docker exec configsvr1 mongosh --eval '
rs.initiate({
  _id: "configRS",
  configsvr: true,
  members: [{ _id: 0, host: "configsvr1:27017" }]
})
'
sleep 3

docker exec shard1svr1 mongosh --eval '
rs.initiate({
  _id: "shard1RS",
  members: [{ _id: 0, host: "shard1svr1:27017" }]
})
'
sleep 3

docker exec shard2svr1 mongosh --eval '
rs.initiate({
  _id: "shard2RS",
  members: [{ _id: 0, host: "shard2svr1:27017" }]
})
'
sleep 5

docker exec mongos mongosh --eval '
sh.addShard("shard1RS/shard1svr1:27017");
sh.addShard("shard2RS/shard2svr1:27017");
'
sleep 3

docker exec mongos mongosh --eval '
sh.enableSharding("online_cinema");
'

docker exec mongos mongosh --eval '
sh.shardCollection("online_cinema.movies", { movie_id: "hashed" });
sh.shardCollection("online_cinema.users", { user_id: "hashed" });
sh.shardCollection("online_cinema.reviews", { user_id: "hashed" });
'

docker exec mongos mongosh --eval 'sh.status()'

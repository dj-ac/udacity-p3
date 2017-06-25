/* Get unique fields from documents in the database
 - https://stackoverflow.com/questions/2298870/mongodb-get-names-of-all-keys-in-collection */
mr = db.runCommand({
  "mapreduce" : "test-collection",
  "map" : function() {
    for (var key in this.tags) { emit(key, null); }
  },
  "reduce" : function(key, stuff) { return null; }, 
  "out": "my_collection" + "_keys"
})
db[mr.result].distinct("_id")
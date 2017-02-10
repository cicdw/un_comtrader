# un_comtrader
For automating requests to the UN comtrade trade database.

### Importing / Setup

To import the module, open Python and run:

```
from uncomtrader import ComtradeRequest
```

### Initialize a Request

There are currently three ways to initialize a UN Comtrade Request:
#### Method 1
This method starts from an empty request and sequentially adds the necessary request attributes.

```
req = ComtraderRequest()
req.type = "C"
req.freq = "A"
req.time_period = [2014,2015,2016]
req.reporting area = "all"
req.partner_area = 36
req.hs = [44,4401,4402]
```

#### Method 2
This method sets all of the attributes upon initialization.

```
req = ComtraderRequest(type = "C", freq = "A", time_period = [2014,2015,2016] reporting_area = "all", partner_area = 36, hs = [44,4401,4402])
```

#### Method 3
This method intializes a request from a json file.

```
file_loc = "path/to/json/file.json" # example .json is in data/ directory in repo
req = ComtraderRequest.from_file(file_loc)
```

### Pull data

There are currently two methods to pull data from UN Comtrade.

#### Method 1
This method pulls data and returns it as a pandas dataframe.

```
df = req.pull_data()
df.head()
```

This data can then be saved with:

```
df.to_csv("path/to/where/you/want/tosave.csv")
```

#### Method 2
This method pulls data and saves it as a csv or json.

```
req.pull_data(save = "path/to/where/you/want/tosave.csv")
```

Note that the data is still available by calling

```
df = req.data
```

### Help

```
help(req)
```

OR

```
help(ComtradeRequest)
```

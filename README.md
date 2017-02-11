# uncomtrader
For automating requests to the [UN comtrade trade database](https://comtrade.un.org), which is a repository of official international trade statistics and relevant analytical tables.

### Installation

To install, clone the repo and run `setup.py`:

```
git clone https://github.com/moody-marlin/un_comtrader.git
cd un_comtrader
python setup.py
```

OR use `pip`:

```
pip install git+https://github.com/moody-marlin/un_comtrader.git
```

### Importing

To import the module, open Python and run:

```python
>>> from uncomtrader import ComtradeRequest
```

### Initialize a Request

There are currently three ways to initialize a UN Comtrade Request:
#### Method 1
This method starts from an empty request and sequentially adds the necessary request attributes.

```python
>>> req = ComtradeRequest()
>>> req.type = "C"
>>> req.freq = "A"
>>> req.time_period = [2014,2015,2016]
>>> req.reporting area = "all"
>>> req.partner_area = 36
>>> req.hs = [44,4401,4402]
```

#### Method 2
This method sets all of the attributes upon initialization.

```python
>>> req = ComtradeRequest(type = "C", freq = "A", time_period = [2014,2015,2016],\
...             reporting_area = "all", partner_area = 36, hs = [44,4401,4402])
```

#### Method 3
This method intializes a request from a json file.

```python
>>> file_loc = "path/to/json/file.json" # example .json is in data/ directory in repo
>>> req = ComtradeRequest.from_file(file_loc)
```

### Pull data

There are currently two methods to pull data from UN Comtrade.

#### Method 1
This method pulls data and returns it as a pandas dataframe.

```python
>>> df = req.pull_data()
>>> df.head()
```

This data can then be saved with:

```python
>>> df.to_csv("path/to/where/you/want/tosave.csv")
```

#### Method 2
This method pulls data and saves it as a csv or json.

```python
>>> req.pull_data(save = "path/to/where/you/want/tosave.csv")
```

Note that the data is still available by calling

```python
>>> df = req.data
```

### Large Requests

If your single data request violates the [usage limits](https://comtrade.un.org/data/doc/api/), a `MultiRequest` is necessary; the syntax remains the same, but `MultiRequest` is capable of breaking your requests into smaller allowable requests; there are two ways to initialize a MultiRequest, but the recommended way is from a `.json` file:

```python
>>> from uncomtrader import MultiRequest
>>> req = MultiRequest.from_file("data/multirequest.json") #found in the repo
>>> print(req)
Currently storing 2 Comtrade Requests with URLs:
http://comtrade.un.org/api/get?fmt=csv&p=36&r=all&ps=2011,2012,2013,2014,2015&px=HS&cc=44,4401&freq=A&type=C
http://comtrade.un.org/api/get?fmt=csv&p=36&r=all&ps=2016&px=HS&cc=44,4401&freq=A&type=C
>>> data = req.pull_data()
```

### Help

```python
>>> help(req)
```

OR

```python
>>> help(ComtradeRequest)
```

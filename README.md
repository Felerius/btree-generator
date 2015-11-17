# A graph generator for B+ trees
![Image of a rendered B+ tree](https://github.com/Felerius/btree-generator/raw/master/images/main.png)

This is a python script for generating graphs in the [DOT language](https://en.wikipedia.org/wiki/DOT_(graph_description_language)) representing B+ trees.

## Installation

You only need the [btree.py](btree.py) script.
The script was developed with [Python 3.4](http://python.org) and up in mind, but it might also work with earlier version of Python 3.x.
It depends on the [PyYAML library](http://pyyaml.org/), which you can easily install by running `pip install pyyaml`.

## Usage

Assuming you have a data file containing the data of the B+ tree (see below for the format), usage is as simple as running:
```sh
./btree.py tree.yml
```

This will print DOT code to the terminal.
This can be converted to a finished graph using a tool like [Graphviz](http://graphviz.org). For example:
```sh
./btree tree.yml | dot -Tsvg > tree.svg
```

## Data file format

![Image of a simple rendered B+ tree](https://github.com/Felerius/btree-generator/raw/master/images/simple.png)

If you are unfamiliar with the YAML syntax, you might want to check out the [YAML website](http://yaml.org) first.

The simple tree above was generated from the following YAML code:
```yaml
keys_per_block: 2
tree:
  keys: [3, 6]
  children:
    - [1]
    - [3, 5]
    - [6, 8]
```

On the top level, there is an attribute named `keys_per_block` specifying the maximum number of keys per block.
Another attribute named `tree` contains the actual tree data.
Each block has two attributes:
  - `keys`, a list of keys contained in the block.
    You can leave out empty keys here, the block will be automatically filled up with underscores to represent missing keys, as you can see in the leftmost leaf.
  - `children`, a list of child blocks.
  
For leaf blocks you can just specify the block as a list containing the keys, as has been done here for all leaves.

### Omitting parts of the tree
![Image of a B+ tree with parts of the tree omitted](https://github.com/Felerius/btree-generator/raw/master/images/omitting_subtrees.png)

When graphing larger trees, it might be interesting to leave out parts of the B+ tree.
This can be achieved by simply placing placeholder blocks and completely leaving out their children (the graph above was generated from [this data file](examples/omitting_subtrees.yml)).

The generation of pointers between leaves will also be adjusted.
In the image above the pointer between `[11, 13]` and the `[67, 69]` block has been omitted, because due to the structure of B+ trees there must be other leaves in the omitted middle part of the tree, and therefore the two blocks would not be directly connected.

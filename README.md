# Avalanche
Realtime and Online Model Development Framework


## Quick Overview

Avalanche is a framework that helps data analysts of the world implement their realtime models in a modular and distributed fashion. It is currently written in Python and leverages the mighty power of ZMQ streams. It technically helps you define a pipeline made of data processing nodes and stream connection edges. The edges connect the nodes and control how the data runs through the pipelines; the nodes process the data in your desired fashion.

## How to use

Let's take a more practical look at the tool:

<pre><code>$ git clone https://github.com/ThibaultReuille/avalanche.git
$ cd avalanche
$ ./avalanche.py pipelines/default.json
</code></pre>

Your are now running the default processing graph! It doesn't do much for now but this is about to change. We will now take a look at our default pipeline and understand how to manipulate it to make it do what we want.

[Default Avalanche Pipeline](https://github.com/ThibaultReuille/avalanche/blob/master/pipelines/default.json "Default Avalanche Pipeline") 

This default pipeline configuration consists of 3 parts:

- Attributes: This part defines the general environment of the stream graph. In particular, it can load the various plugins used in your pipeline.

- Nodes: In this part, you can define all the processing nodes. In practice, each node will usually receive incoming messages, process them and send them through the pipeline. 

- Edges : This is where you connect the different nodes together and connect them to create your full data processing pipeline.

Great! Now you know how to virtually define your full message processing pipeline with Avalanche! Let us dig deeper and explore how to create your own custom models.

## Write your own plugin

For a more accurate description, let's refer to our plugin template:

[Avalanche Plugin Template](https://github.com/ThibaultReuille/avalanche/blob/master/plugins/template.json "Avalanche Plugin Template") 

For the most part, the comments in this template file are self-explanatory. However we may simply add that each node plugin will loaded and bound to its node. The node information and members can be retrieved either in the constructor or through the node instance. The node processing code will run in its own thread and will receive/send info through the input/output node streams. The plugin definition interface is easy and simple enough for you to implement any kind of metrics, models, filters or any other realtime pipeline element.

The rest is up to you!


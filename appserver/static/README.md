# Splunk REST API Modular Input v1.3.9

## Overview

This is a Splunk modular input add-on for polling REST APIs.


## Features

* Perform HTTP(s) GET requests to REST endpoints and output the responses to Splunk
* Multiple authentication mechanisms
* Add custom HTTP(s) Header properties
* Add custom URL arguments
* HTTP(s) Streaming Requests
* HTTP(s) Proxy support , supports HTTP CONNECT Verb
* Response regex patterns to filter out responses
* Configurable polling interval
* Configurable timeouts
* Configurable indexing of error codes
* Persist and retrieve cookies

### Authentication

The following authentication mechanisms are supported:

* None
* HTTP Basic
* HTTP Digest
* OAuth1
* OAuth2 (with auto refresh of the access token)
* Custom


### Custom Authentication Handlers

You can provide your own custom Authentication Handler. This is a Python class that you should add to the 
rest_ta/bin/authhandlers.py module.

http://docs.python-requests.org/en/latest/user/advanced/#custom-authentication

You can then declare this class name and any parameters in the REST Input setup page.

### Custom Response Handlers

You can provide your own custom Response Handler. This is a Python class that you should add to the 
rest_ta/bin/responsehandlers.py module.

You can then declare this class name and any parameters in the REST Input setup page.

#Token substitution in Endpoint URL

There is support for dynamic token substitution in the endpoint URL

ie : /someurl/foo/$sometoken$/goo 

$sometoken$ will get substituted with the output of the 'sometoken' function in bin/tokens.py

So you can add you own tokens simply by adding a function to bin/tokens.py

Currenty there is 1 token implemented , $datetoday$ , which will resolve to today's date in format "2014-02-18"

Token replacement functions in the URL can also return a list of values, that will cause 
multiple URL's to be formed and the requests for these URL's will be executed in parallel in multiple threads. 

## Dependencies

* Splunk 5.0+
* Supported on Windows, Linux, MacOS, Solaris, FreeBSD, HP-UX, AIX

## Setup

* Untar the release to your $SPLUNK_HOME/etc/apps directory
* Restart Splunk
* Browse to Manager -> Data Inputs -> REST and setup your inputs


## Logging

Any log entries/errors will get written to $SPLUNK_HOME/var/log/splunk/splunkd.log


## Troubleshooting

* You are using Splunk 5+
* Look for any errors in $SPLUNK_HOME/var/log/splunk/splunkd.log
* Any firewalls blocking outgoing HTTP calls
* Is your REST URL, headers, url arguments correct
* Is you authentication setup correctly

## Contact

This project was initiated by Damien Dallimore
<table>

<tr>
<td><em>Email</em></td>
<td>ddallimore@splunk.com</td>
</tr>

</table>
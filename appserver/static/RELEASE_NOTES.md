1.4
----
Delimiter fix

1.3.9
-----
Can now declare a CRON pattern for your polling interval.
Multiple requests spawned by tokenization can be declared to run in parallel or sequentially.
Multiple sequential requests can optionally have a stagger time enforced between each request.

1.3.8
-----
Minor code bug with logging

1.3.7
-----
Added support for token replacement functions in the URL to be able to return a list
of values, that will cause multiple URL's to be formed and the requests for these
URL's will be executed in parallel in multiple threads. See tokens.py

1.3.6
-----

Added a custom response handler for rolling out generic JSON arrays
Refactored key=value delimited string handling to only split on the first "=" delimiter

1.3.5
-----

Ensure that token substitution in the endpoint URL is dynamically applied for each
HTTP request

1.3.4
-----

Added support for dynamic token substitution in the endpoint URL

ie : /someurl/foo/$sometoken$/goo 

$sometoken$ will get substituted with the output of the 'sometoken' function
in bin/tokens.py

1.3.3
-----
Added support to persist and retrieve cookies

1.3.2
-----
Changed the logic for persistence of state back to inputs.conf to occur directly after polling/event indexing has completed rather than waiting for the polling loop frequency sleep period to exit. This potentially deals with situations where you might terminate Splunk before the REST Mod Input has persisted state changes back to inputs.conf because it was in a sleep loop during shutdown.
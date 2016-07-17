Splunk-logshare is a Splunk Modular Input forked from https://splunkbase.splunk.com/app/1546/.

It allows you to inject logs from CloudFlare's logshare into Splunk automatically.

# Installation

To install:

Clone this into your $SPLUNK/etc/apps as cloudflare:

```
git clone https://github.com/justinbatcf/splunk-logshare.git /opt/splunk/etc/apps/cloudflare
```

Restart Splunk.

# Configuration

Create a source type for ELS either through the web interface or by creating $SPLUNK/etc/system/local/props.conf:

```
[ELS]
DATETIME_CONFIG =
INDEXED_EXTRACTIONS = json
KV_MODE = none
NO_BINARY_CHECK = true
TIME_FORMAT = %s%9N
category = Structured
description = CloudFlare Enterprise Log Share
disabled = false
pulldown_type = true
TIMESTAMP_FIELDS = timestamp
TZ = UTC
MAX_TIMESTAMP_LOOKAHEAD = 10000
```

Configure a new Data Input for the new CloudFlare Log Share data input type. Leave the ray id field blank, unless you have a specific ray id you want to start from.

Set the sourcetype to the source you created, in this case ELS.

We recommend creating a special user with logs-only privileges for downloading logs.

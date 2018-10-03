# PANDORA

Small app basis composed from the following technologies:

* [Dgraph](https://dgraph.io/) as data store with GraphQL support, write operations using REST
* [tusd](https://tus.io/) as file store service baked by Amazon S3 compatible storage like [Minio](https://www.minio.io/)
* [Elasticsearch](https://www.elastic.co/products/elasticsearch) as search engine. Dgraph data is automatically replicated in elasticseach index - not implemented yet :)
* [Kibana](https://www.elastic.co/products/kibana) to visualize Elasticsearch data
* [nats](https://nats.io/) as messaging system with streaming push notifications via [SSE](https://en.wikipedia.org/wiki/Server-sent_events) channel

## Basic Idea

Simple, Flexible, Dynamic, Declarative, Reactive, Realtime Information System :)

## How to run

`docker-compose up` runs all app services:

* `zero` - Dgraph cluster manager
* `dgraph` - Dgraph data manager hosts predicates & indexes
* `ratel` - serves the UI to run queries, mutations & altering schema
* `nats` - message bus
* `minio` - Amazon S3 compatible file store
* `elasticsearch` - search and analitycs engine
* `kibana` - Elasticsearch dashboard
* `app` - Application API service
* `caddy` - Web Server as service gateway

## How to build

* `dep ensure`
* `go install`

## How to run tests

* `go test -coverprofile cover.out`
* `go tool cover -html cover.out`

# Retriever
This repository contains the source code of the Retriever module developed within the WP3 of the SALTED Project. The aim of this module is the forwarding of requests to the Context Broker and provision of different format representations, as part of the CKAN connector. To this end, this component enables two URL resources for each type of request allowed (see [Usage](#usage)).

## Usage
As mentioned previously, this Retriever module does the forwarding of requests, acting then as a proxy. The two URL resources accessible for this module are:
- `/retriever/realtime/__<entity_type>__.<representation_format>`

    This resource allows the query of realtime data (i.e. last records) for a specific data type in a specific format. 
    Example:
    ```
    GET /retriever/realtime/__https%3A%2F%2Fsmartdatamodels.org%2FdataModel.Battery%2FBatteryStatus__.json
    ```
    This request will perform the next query to the Context Broker:
    ```
    GET  /entities?type=https%3A%2F%2Fsmartdatamodels.org%2FdataModel.Battery%2FBatteryStatus
    Accept: application/json
    ```

- `/temporal/__<entity_type>__.<representation_format>?<temporal_unit>=<value>}`, with `temporal_unit = ["year", "months", "weeks", "days", "hours"]`

    This resource allows the query of temporal data (i.e. temporal records) for a specific data type in a specific format. 
    Example:
    ```
    GET /retriever/temporal/__https%3A%2F%2Fsmartdatamodels.org%2FdataModel.Battery%2FBatteryStatus__.jsonld?days=5
    ```
    This request will perform the next query to the Context Broker:
    ```
    GET  /temporal/entities?type=https%3A%2F%2Fsmartdatamodels.org%2FdataModel.Battery%2FBatteryStatus&timerel=after&timeAt=<date>
    Accept: application/ld+json
    # with <date> = datetime.now()-5 days
    ```


## Installation
Once you have the repository code in your machine, follow the next steps:
1. Create a `.env` file and add your information (parameters to change: `EXTERNAL_PORT`, `INTERNAL_PORT`, `HOST_NAME`).
    ```bash
    cp .env.template .env
    ```

3. Create a `config.json` file and set up the variables to your needs.
    ```bash
    cp config.json.template config.json
    ```

4. Deploy the docker
    ```bash
    docker-compose -f docker-compose.yml build
    docker-compose -f docker-compose.yml up

    # or do it together
    docker-compose -f docker-compose.yml up --build
    ```


## Authors
The Retriever module has been written by:
- [Laura Martín](https://github.com/lauramartingonzalezzz)
- [Jorge Lanza](https://github.com/jlanza)
- [Víctor González](https://github.com/vgonzalez7)
- [Juan Ramón Santana](https://github.com/juanrasantana)
- [Pablo Sotres](https://github.com/psotres)
- [Luis Sánchez](https://github.com/sanchezgl)


## Acknowledgement
This work was supported by the European Commission CEF Programme by means of the project SALTED "Situation-Aware Linked heTerogeneous Enriched Data" under the Action Number 2020-EU-IA-0274.


## License
This material is licensed under the GNU Lesser General Public License v3.0 whose full text may be found at the *LICENSE* file.

It mainly makes use of the following libraries and frameworks (dependencies of dependencies have been omitted):

| Library / Framework |   License    |
|---------------------|--------------|
| Flask          | BSD          |
| python_dateutil             | Apache Software License and BSD License          |
| Requests                 | Apache 2.0          |
| tokenhandler          |  TBD          |
| waitress          | ZPL 2.1          |